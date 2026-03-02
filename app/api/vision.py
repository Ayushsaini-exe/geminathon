"""
Vision Disease Detection API routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.vision import DiseaseDetectionRequest, DiseaseDetectionResponse
from app.services.vision_service import VisionService
from database.session import get_db

router = APIRouter(prefix="/api/vision", tags=["Disease Detection"])
_service = VisionService()


@router.post("/detect", response_model=DiseaseDetectionResponse)
async def detect_disease(
    request: DiseaseDetectionRequest, db: AsyncSession = Depends(get_db)
):
    """Detect crop disease from an uploaded image."""
    return await _service.detect_disease(request, db)
