"""
Soil Health Card (SHC) API routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.shc import SHCRequest, SHCResponse
from app.services.shc_service import SHCService
from database.session import get_db

router = APIRouter(prefix="/api/shc", tags=["Soil Health Card"])
_service = SHCService()


@router.post("/fetch", response_model=SHCResponse)
async def fetch_soil_profile(
    request: SHCRequest, db: AsyncSession = Depends(get_db)
):
    """Fetch soil health card data and generate fertilizer advice."""
    return await _service.fetch_soil_profile(request, db)
