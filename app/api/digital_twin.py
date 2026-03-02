"""
Digital Twin Visualization Engine API routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.digital_twin import (
    DigitalTwinUpdateRequest,
    DigitalTwinResponse,
)
from app.services.digital_twin_service import DigitalTwinService
from database.session import get_db

router = APIRouter(prefix="/api/digital-twin", tags=["Digital Twin"])
_service = DigitalTwinService()


@router.post("/update", response_model=DigitalTwinResponse)
async def update_zone(
    request: DigitalTwinUpdateRequest, db: AsyncSession = Depends(get_db)
):
    """Add or update a risk zone on the farm digital twin."""
    return await _service.update_zone(request, db)


@router.get("/map/{farmer_id}", response_model=DigitalTwinResponse)
async def get_farm_map(
    farmer_id: str, db: AsyncSession = Depends(get_db)
):
    """Get the full digital twin map for a farmer."""
    return await _service.get_farm_map(farmer_id, db)
