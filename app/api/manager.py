"""
Manager-only API routes — aggregate views and farmer management.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_role
from database.models import User, Farmer, ESGScore, DiseaseDetection, SustainabilityReport
from database.session import get_db

router = APIRouter(prefix="/api/manager", tags=["Manager"])


@router.get("/farmers")
async def list_all_farmers(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("manager")),
):
    """List all farmers with basic stats (manager-only)."""
    result = await db.execute(select(Farmer).order_by(Farmer.created_at.desc()).limit(200))
    farmers = result.scalars().all()

    items = []
    for f in farmers:
        items.append({
            "id": f.id,
            "name": f.name,
            "phone": f.phone,
            "location": f.location,
            "language": f.language,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        })
    return {"farmers": items, "total": len(items)}


@router.get("/stats")
async def get_platform_stats(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("manager")),
):
    """Aggregate platform statistics (manager-only)."""
    farmer_count = (await db.execute(select(func.count(Farmer.id)))).scalar() or 0
    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    disease_count = (await db.execute(select(func.count(DiseaseDetection.id)))).scalar() or 0
    report_count = (await db.execute(select(func.count(SustainabilityReport.id)))).scalar() or 0

    # Avg ESG score
    avg_esg = (await db.execute(select(func.avg(ESGScore.score)))).scalar()

    return {
        "total_farmers": farmer_count,
        "total_users": user_count,
        "total_disease_scans": disease_count,
        "total_reports": report_count,
        "avg_esg_score": round(avg_esg, 2) if avg_esg else 0,
    }
