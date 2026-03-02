"""
Sustainability Report Generator API routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.report import ReportRequest, ReportResponse
from app.services.report_service import ReportService
from database.session import get_db

router = APIRouter(prefix="/api/report", tags=["Report Generator"])
_service = ReportService()


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest, db: AsyncSession = Depends(get_db)
):
    """Generate a sustainability report PDF with QR verification."""
    return await _service.generate(request, db)
