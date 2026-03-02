"""
ESG & Sustainability Scoring Engine API routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.esg import ESGActionRequest, ESGScoreResponse, ESGHistoryResponse
from app.services.esg_engine import ESGEngine
from database.session import get_db

router = APIRouter(prefix="/api/esg", tags=["ESG Scoring"])
_service = ESGEngine()


@router.post("/action", response_model=ESGScoreResponse)
async def log_esg_action(
    request: ESGActionRequest, db: AsyncSession = Depends(get_db)
):
    """Log a sustainability action and get updated ESG score."""
    return await _service.log_action(request, db)


@router.get("/score/{farmer_id}", response_model=ESGScoreResponse)
async def get_esg_score(
    farmer_id: str, db: AsyncSession = Depends(get_db)
):
    """Get current ESG score for a farmer."""
    return await _service.get_score(farmer_id, db)


@router.get("/history/{farmer_id}", response_model=ESGHistoryResponse)
async def get_esg_history(
    farmer_id: str, db: AsyncSession = Depends(get_db)
):
    """Get ESG score history for trend analysis."""
    return await _service.get_history(farmer_id, db)
