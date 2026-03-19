"""
Vision Disease Detection Service.

Uses a ResNet9 model trained on the PlantVillage dataset (38 disease classes)
for crop disease classification, and integrates with Gemini for treatment plans.
"""

import base64
import io
import os

from PIL import Image
from google import genai
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import logger
from app.schemas.vision import DiseaseDetectionRequest, DiseaseDetectionResponse
from database.models import DiseaseDetection


# ---------------------------------------------------------------------------
# PlantVillage 38-class labels (alphabetical, matching training dataset)
# ---------------------------------------------------------------------------
DISEASE_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot_Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites_Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

# Model weights path
MODEL_SD_PATH = os.path.join("app", "models", "plant-disease-model-state-dict.pth")


# ---------------------------------------------------------------------------
# Lazy torch imports + ResNet9 architecture (matches training code)
# ---------------------------------------------------------------------------

def _lazy_import_torch():
    """Lazy-import torch and torchvision to avoid startup failure."""
    try:
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
        from torchvision import transforms
        return torch, nn, F, transforms
    except ImportError:
        raise ImportError(
            "torch and torchvision are required for disease detection. "
            "Install them with: pip install torch torchvision"
        )


def _build_resnet9(num_classes: int = 38):
    """Build the ResNet9 architecture matching the trained model."""
    import torch.nn as nn

    def conv_block(in_channels, out_channels, pool=False):
        layers = [
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        ]
        if pool:
            layers.append(nn.MaxPool2d(2))
        return nn.Sequential(*layers)

    class ResNet9(nn.Module):
        def __init__(self, in_channels, num_classes):
            super().__init__()
            self.conv1 = conv_block(in_channels, 64)
            self.conv2 = conv_block(64, 128, pool=True)
            self.res1 = nn.Sequential(conv_block(128, 128), conv_block(128, 128))
            self.conv3 = conv_block(128, 256, pool=True)
            self.conv4 = conv_block(256, 512, pool=True)
            self.res2 = nn.Sequential(conv_block(512, 512), conv_block(512, 512))
            self.classifier = nn.Sequential(
                nn.MaxPool2d(4),
                nn.Flatten(),
                nn.Linear(512, num_classes),
            )

        def forward(self, xb):
            out = self.conv1(xb)
            out = self.conv2(out)
            out = self.res1(out) + out
            out = self.conv3(out)
            out = self.conv4(out)
            out = self.res2(out) + out
            out = self.classifier(out)
            return out

    return ResNet9(3, num_classes)


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class VisionService:
    """ResNet9-based crop disease detection with Gemini treatment plans."""

    def __init__(self):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-2.0-flash"
        self._torch = None
        self._device = None
        self._model = None
        self._transform = None

    def _ensure_torch(self):
        """Initialize torch components on first use."""
        if self._torch is None:
            torch, nn, F, transforms = _lazy_import_torch()
            self._torch = torch
            self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self._transform = transforms.Compose([
                transforms.Resize((32, 32)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ])

    def _get_model(self):
        """Load the trained PlantVillage ResNet9 model."""
        self._ensure_torch()
        if self._model is None:
            model = _build_resnet9(num_classes=len(DISEASE_CLASSES))

            if os.path.exists(MODEL_SD_PATH):
                state = self._torch.load(
                    MODEL_SD_PATH,
                    map_location=self._device,
                    weights_only=True,
                )
                model.load_state_dict(state)
                logger.info(f"✅ Loaded trained model from {MODEL_SD_PATH}")
            else:
                logger.warning("⚠️ No model file found — using random weights")

            model.to(self._device)
            model.eval()
            self._model = model
            logger.info(
                f"Vision model ready on {self._device} with "
                f"{len(DISEASE_CLASSES)} disease classes"
            )
        return self._model

    async def detect_disease(
        self, request: DiseaseDetectionRequest, db: AsyncSession
    ) -> DiseaseDetectionResponse:
        """
        1. Preprocess image
        2. Run through ResNet9 classifier
        3. Get top prediction
        4. Generate treatment plan via Gemini
        5. Store detection record
        """
        logger.info(f"Disease detection for farmer {request.farmer_id}")

        self._ensure_torch()

        # 1. Decode and preprocess image
        image = self._decode_image(request.image_base64)
        tensor = self._transform(image).unsqueeze(0).to(self._device)

        # 2. Run inference
        model = self._get_model()
        with self._torch.no_grad():
            outputs = model(tensor)
            probabilities = self._torch.softmax(outputs, dim=1)
            confidence, predicted = self._torch.max(probabilities, 1)

        raw_label = DISEASE_CLASSES[predicted.item()]
        conf = round(confidence.item(), 4)

        # Parse the label: "Apple___Cedar_apple_rust" → disease name
        disease = self._format_label(raw_label)

        # 3. Generate treatment plan
        treatment = await self._generate_treatment_plan(
            disease, conf, request.crop_type, raw_label
        )

        # Determine risk level
        risk_level = self._assess_risk(raw_label, conf)

        # 4. Store in database
        detection = DiseaseDetection(
            farmer_id=request.farmer_id,
            disease=disease,
            confidence=conf,
            treatment=treatment,
        )
        db.add(detection)
        await db.flush()

        return DiseaseDetectionResponse(
            disease=disease,
            confidence=conf,
            treatment_plan=treatment,
            risk_level=risk_level,
            digital_twin_updated=True,
        )

    def _decode_image(self, image_base64: str) -> Image.Image:
        """Decode base64 image to PIL Image."""
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        return image

    def _format_label(self, raw_label: str) -> str:
        """
        Convert PlantVillage label to human-readable format.
        'Apple___Cedar_apple_rust' → 'Apple - Cedar Apple Rust'
        'Tomato___healthy' → 'Tomato - Healthy'
        """
        parts = raw_label.split("___")
        crop = parts[0].replace("_", " ")
        condition = parts[1].replace("_", " ").strip() if len(parts) > 1 else "Unknown"
        return f"{crop} - {condition.title()}"

    def _assess_risk(self, raw_label: str, confidence: float) -> str:
        """Determine risk level based on disease type and confidence."""
        if "healthy" in raw_label.lower():
            return "low"

        # High-severity diseases
        high_severity = [
            "Late_blight", "Bacterial_spot", "Citrus_greening",
            "Black_rot", "Leaf_Curl", "mosaic_virus",
        ]
        is_severe = any(d in raw_label for d in high_severity)

        if confidence > 0.85:
            return "critical" if is_severe else "high"
        if confidence > 0.6:
            return "medium"
        return "low"

    async def _generate_treatment_plan(
        self, disease: str, confidence: float, crop_type: str | None, raw_label: str
    ) -> str:
        """Use Gemini to generate a detailed treatment plan."""
        if "healthy" in raw_label.lower():
            return "✅ No disease detected. Your crop looks healthy! Continue current farming practices and monitor regularly."

        try:
            prompt = f"""You are a plant pathologist advising an Indian farmer.

Disease Detected: {disease} (PlantVillage label: {raw_label})
Confidence: {confidence * 100:.1f}%
Crop: {crop_type or disease.split(' - ')[0]}

Provide a concise treatment plan including:
1. Immediate actions to take
2. Recommended fungicides/pesticides (with Indian brand names if possible)
3. Application dosage and method
4. Preventive measures for future
5. Estimated recovery timeline

Keep it practical and actionable for an Indian farmer."""

            response = self.client.models.generate_content(
                model=self.model_name, contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Treatment plan generation failed: {e}")
            return f"Disease: {disease}. Please consult your local agricultural officer for treatment."
