"""
Pesticide Verification API routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.pesticide import PesticideVerifyRequest, PesticideVerifyResponse
from app.services.pesticide_verification_service import PesticideVerificationService
from database.session import get_db

router = APIRouter(prefix="/api/pesticide", tags=["Pesticide Verification"])
_service = PesticideVerificationService()


@router.post("/verify", response_model=PesticideVerifyResponse)
async def verify_pesticide(
    request: PesticideVerifyRequest, db: AsyncSession = Depends(get_db)
):
    """Verify pesticide authenticity via OCR batch ID check."""
    return await _service.verify(request, db)
