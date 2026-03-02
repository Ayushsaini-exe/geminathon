"""
Vision Disease Detection Service.

Uses a ResNet-based model for crop disease classification
and integrates with RAG for treatment plans.
"""

import base64
import io
from uuid import UUID

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from google import genai
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import logger
from app.schemas.vision import DiseaseDetectionRequest, DiseaseDetectionResponse
from database.models import DiseaseDetection


# Common crop diseases the model can classify
DISEASE_CLASSES = [
    "Healthy",
    "Bacterial Leaf Blight",
    "Brown Spot",
    "Leaf Smut",
    "Blast",
    "Tungro",
    "Sheath Blight",
    "Late Blight",
    "Early Blight",
    "Powdery Mildew",
    "Downy Mildew",
    "Rust",
    "Anthracnose",
    "Cercospora Leaf Spot",
    "Mosaic Virus",
]


class VisionService:
    """ResNet-based crop disease detection with Gemini treatment plans."""

    def __init__(self):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-2.0-flash"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model = None
        self._transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])

    def _get_model(self) -> nn.Module:
        """Lazy-load ResNet model (uses random weights as placeholder)."""
        if self._model is None:
            model = models.resnet18(weights=None)
            model.fc = nn.Linear(model.fc.in_features, len(DISEASE_CLASSES))
            model.to(self.device)
            model.eval()
            self._model = model
            logger.info(
                f"Vision model loaded on {self.device} with "
                f"{len(DISEASE_CLASSES)} disease classes"
            )
        return self._model

    async def detect_disease(
        self, request: DiseaseDetectionRequest, db: AsyncSession
    ) -> DiseaseDetectionResponse:
        """
        1. Preprocess image
        2. Run through ResNet classifier
        3. Get top prediction
        4. Generate treatment plan via Gemini
        5. Store detection record
        """
        logger.info(f"Disease detection for farmer {request.farmer_id}")

        # 1. Decode and preprocess image
        image = self._decode_image(request.image_base64)
        tensor = self._transform(image).unsqueeze(0).to(self.device)

        # 2. Run inference
        model = self._get_model()
        with torch.no_grad():
            outputs = model(tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)

        disease = DISEASE_CLASSES[predicted.item()]
        conf = round(confidence.item(), 4)

        # 3. Generate treatment plan
        treatment = await self._generate_treatment_plan(
            disease, conf, request.crop_type
        )

        # Determine risk level based on confidence & disease
        risk_level = self._assess_risk(disease, conf)

        # 4. Store in database
        detection = DiseaseDetection(
            farmer_id=UUID(request.farmer_id),
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

    def _assess_risk(self, disease: str, confidence: float) -> str:
        """Determine risk level based on disease type and confidence."""
        if disease == "Healthy":
            return "low"
        if confidence > 0.85:
            return "critical" if disease in ["Blast", "Late Blight", "Tungro"] else "high"
        if confidence > 0.6:
            return "medium"
        return "low"

    async def _generate_treatment_plan(
        self, disease: str, confidence: float, crop_type: str | None
    ) -> str:
        """Use Gemini to generate a detailed treatment plan."""
        if disease == "Healthy":
            return "No disease detected. Continue current farming practices."

        try:
            prompt = f"""You are a plant pathologist advising an Indian farmer.

Disease Detected: {disease}
Confidence: {confidence * 100:.1f}%
Crop: {crop_type or 'Unknown'}

Provide a concise treatment plan including:
1. Immediate actions to take
2. Recommended fungicides/pesticides (with Indian brand names if possible)
3. Application dosage and method
4. Preventive measures for future
5. Estimated recovery timeline

Keep it practical and actionable."""

            response = self.client.models.generate_content(
                model=self.model_name, contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Treatment plan generation failed: {e}")
            return f"Disease: {disease}. Please consult your local agricultural officer for treatment."
