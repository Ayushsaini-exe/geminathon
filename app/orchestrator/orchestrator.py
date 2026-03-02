"""
AI Orchestrator — the central brain of AgroFix.

Detects user intent via Gemini, routes to the correct service module,
merges context from memory, and returns structured JSON responses.
"""

import json
from uuid import UUID

from google import genai
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import logger
from app.schemas.orchestrator import OrchestratorRequest, OrchestratorResponse
from app.services.rag_service import RAGService
from app.services.shc_service import SHCService
from app.services.pesticide_verification_service import PesticideVerificationService
from app.services.vision_service import VisionService
from app.services.harvest_engine import HarvestEngine
from app.services.esg_engine import ESGEngine
from app.services.digital_twin_service import DigitalTwinService
from app.services.report_service import ReportService
from app.schemas.rag import RAGQueryRequest
from app.schemas.shc import SHCRequest
from app.schemas.pesticide import PesticideVerifyRequest
from app.schemas.vision import DiseaseDetectionRequest
from app.schemas.harvest import HarvestRequest
from app.schemas.esg import ESGActionRequest
from app.schemas.report import ReportRequest
from database.models import ChatHistory


# Intent categories mapped to modules
INTENT_MAP = {
    "advisory": "rag",
    "soil_health": "shc",
    "pesticide_check": "pesticide",
    "disease_detection": "vision",
    "harvest_timing": "harvest",
    "sustainability": "esg",
    "report": "report",
    "digital_twin": "digital_twin",
    "general": "rag",
}


class Orchestrator:
    """Central AI orchestrator — intent classification + module routing."""

    def __init__(self):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-2.0-flash"

        # Service instances
        self.rag = RAGService()
        self.shc = SHCService()
        self.pesticide = PesticideVerificationService()
        self.vision = VisionService()
        self.harvest = HarvestEngine()
        self.esg = ESGEngine()
        self.digital_twin = DigitalTwinService()
        self.report = ReportService()

    async def process(
        self, request: OrchestratorRequest, db: AsyncSession
    ) -> OrchestratorResponse:
        """
        Main orchestration pipeline:
        1. Classify intent
        2. Fetch context memory
        3. Route to module
        4. Merge response with context
        5. Store conversation turn
        """
        logger.info(f"Orchestrator processing: {request.message[:100]}")

        # 1. Classify intent
        intent = await self._classify_intent(request.message, request.image_base64)
        logger.info(f"Detected intent: {intent}")

        # 2. Fetch recent context
        context = await self._get_context(request.farmer_id, db)

        # 3. Route to the appropriate module
        module_name = INTENT_MAP.get(intent, "rag")
        response_data = await self._route(
            intent, module_name, request, db
        )

        # 4. Store orchestrator turn in memory
        await self._store_turn(request.farmer_id, request.message, intent, db)

        return OrchestratorResponse(
            intent=intent,
            module=module_name,
            response=response_data,
            context_summary=f"Processed via {module_name} module with {len(context)} prior interactions",
        )

    async def _classify_intent(
        self, message: str, has_image: str | None
    ) -> str:
        """Use Gemini to classify the user's intent."""
        try:
            # If image is attached, likely disease or pesticide
            image_hint = ""
            if has_image:
                image_hint = " The user has also attached an image."

            prompt = f"""Classify the following farmer message into exactly ONE category.

Categories:
- advisory: General crop advice, fertilizer recommendations, farming tips
- soil_health: Soil testing, SHC card, soil parameters
- pesticide_check: Verify pesticide authenticity, check batch ID, chemical verification
- disease_detection: Crop disease, leaf damage, plant health issues
- harvest_timing: When to harvest, market prices, mandi rates
- sustainability: ESG score, environmental impact, sustainability practices
- report: Generate report, download report, audit document
- digital_twin: Farm map, risk zones, field health visualization
- general: Greetings, unclear intent, chitchat

Message: "{message}"{image_hint}

Respond with ONLY the category name, nothing else."""

            response = self.client.models.generate_content(
                model=self.model_name, contents=prompt
            )
            intent = response.text.strip().lower().replace('"', "").replace("'", "")

            if intent in INTENT_MAP:
                return intent
            return "general"

        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return "general"

    async def _get_context(self, farmer_id: str, db: AsyncSession) -> list[dict]:
        """Fetch recent chat history for context."""
        try:
            stmt = (
                select(ChatHistory)
                .where(ChatHistory.farmer_id == UUID(farmer_id))
                .order_by(ChatHistory.timestamp.desc())
                .limit(10)
            )
            result = await db.execute(stmt)
            records = result.scalars().all()
            return [
                {"role": r.role, "message": r.message[:200]}
                for r in reversed(records)
            ]
        except Exception as e:
            logger.warning(f"Context fetch failed: {e}")
            return []

    async def _route(
        self,
        intent: str,
        module: str,
        request: OrchestratorRequest,
        db: AsyncSession,
    ):
        """Route request to the appropriate service module."""
        try:
            if module == "rag" or module == "general":
                req = RAGQueryRequest(
                    farmer_id=request.farmer_id,
                    question=request.message,
                )
                result = await self.rag.query(req, db)
                return result.model_dump()

            elif module == "shc":
                # Extract SHC ID from message or metadata
                shc_id = request.metadata.get("shc_id", "DEFAULT-SHC-001")
                req = SHCRequest(farmer_id=request.farmer_id, shc_id=shc_id)
                result = await self.shc.fetch_soil_profile(req, db)
                return result.model_dump()

            elif module == "pesticide":
                req = PesticideVerifyRequest(
                    farmer_id=request.farmer_id,
                    image_base64=request.image_base64,
                    batch_id=request.metadata.get("batch_id"),
                )
                result = await self.pesticide.verify(req, db)
                return result.model_dump()

            elif module == "vision":
                if not request.image_base64:
                    return {"error": "Image is required for disease detection"}
                req = DiseaseDetectionRequest(
                    farmer_id=request.farmer_id,
                    image_base64=request.image_base64,
                    crop_type=request.metadata.get("crop_type"),
                )
                result = await self.vision.detect_disease(req, db)
                return result.model_dump()

            elif module == "harvest":
                req = HarvestRequest(
                    farmer_id=request.farmer_id,
                    crop=request.metadata.get("crop", "rice"),
                    location=request.metadata.get("location", "Delhi"),
                )
                result = await self.harvest.analyze(req, db)
                return result.model_dump()

            elif module == "esg":
                req = ESGActionRequest(
                    farmer_id=request.farmer_id,
                    action_type=request.metadata.get("action_type", "organic_fertilizer"),
                    details=request.metadata.get("details", {}),
                )
                result = await self.esg.log_action(req, db)
                return result.model_dump()

            elif module == "report":
                req = ReportRequest(farmer_id=request.farmer_id)
                result = await self.report.generate(req, db)
                return result.model_dump()

            elif module == "digital_twin":
                result = await self.digital_twin.get_farm_map(
                    request.farmer_id, db
                )
                return result.model_dump()

            else:
                return {"message": "I'm not sure how to help with that. Could you rephrase?"}

        except Exception as e:
            logger.error(f"Module routing error ({module}): {e}")
            return {"error": str(e), "module": module}

    async def _store_turn(
        self, farmer_id: str, message: str, intent: str, db: AsyncSession
    ):
        """Store the orchestrator interaction in chat history."""
        try:
            turn = ChatHistory(
                farmer_id=UUID(farmer_id),
                role="system",
                message=f"[Orchestrator] Intent: {intent} | Message: {message[:200]}",
                context={"intent": intent},
            )
            db.add(turn)
            await db.flush()
        except Exception as e:
            logger.warning(f"Failed to store orchestrator turn: {e}")
