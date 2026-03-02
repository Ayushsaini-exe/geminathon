"""
AI Orchestrator API routes — unified endpoint.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.orchestrator import OrchestratorRequest, OrchestratorResponse
from app.orchestrator.orchestrator import Orchestrator
from database.session import get_db

router = APIRouter(prefix="/api/orchestrator", tags=["AI Orchestrator"])
_orchestrator = Orchestrator()


@router.post("/chat", response_model=OrchestratorResponse)
async def chat(
    request: OrchestratorRequest, db: AsyncSession = Depends(get_db)
):
    """Unified AI chat endpoint — detects intent and routes to the correct module."""
    return await _orchestrator.process(request, db)
