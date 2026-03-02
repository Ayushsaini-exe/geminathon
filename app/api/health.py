"""
Health check API endpoint.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "service": "AgroFix AI Platform"}
