"""
Harvest Window Arbitrage Engine API routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.harvest import HarvestRequest, HarvestResponse
from app.services.harvest_engine import HarvestEngine
from database.session import get_db

router = APIRouter(prefix="/api/harvest", tags=["Harvest Engine"])
_service = HarvestEngine()


@router.post("/analyze", response_model=HarvestResponse)
async def analyze_harvest(
    request: HarvestRequest, db: AsyncSession = Depends(get_db)
):
    """Simulate harvest scenarios and get AI recommendation."""
    return await _service.analyze(request, db)
