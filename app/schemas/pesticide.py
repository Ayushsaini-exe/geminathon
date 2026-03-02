"""
Pydantic schemas for Pesticide Authenticity Verification.
"""

from pydantic import BaseModel, Field


class PesticideVerifyRequest(BaseModel):
    """Request to verify a pesticide product."""
    farmer_id: str = Field(..., description="UUID of the farmer")
    image_base64: str | None = Field(None, description="Base64-encoded bottle image")
    batch_id: str | None = Field(None, description="Manually entered batch ID")


class PesticideVerifyResponse(BaseModel):
    """Response with verification result."""
    batch_id: str
    product_name: str | None = None
    manufacturer: str | None = None
    verified: bool
    status: str = Field(..., description="verified | counterfeit | unknown")
    message: str
    ocr_extracted_text: str | None = None
