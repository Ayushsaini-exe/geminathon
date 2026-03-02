"""
Pydantic schemas for Vision Disease Detection.
"""

from pydantic import BaseModel, Field


class DiseaseDetectionRequest(BaseModel):
    """Request with crop image for disease analysis."""
    farmer_id: str = Field(..., description="UUID of the farmer")
    image_base64: str = Field(..., description="Base64-encoded crop image")
    crop_type: str | None = Field(None, description="Known crop type")


class DiseaseDetectionResponse(BaseModel):
    """Response with disease diagnosis."""
    disease: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    treatment_plan: str | None = None
    risk_level: str = "medium"
    digital_twin_updated: bool = False
