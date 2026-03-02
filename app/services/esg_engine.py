"""
ESG & Sustainability Scoring Engine.

Maintains per-farmer sustainability scores across three pillars:
Environmental, Social, and Governance. Updates scores based on
farming actions and tracks historical trends.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.schemas.esg import ESGActionRequest, ESGScoreResponse, ESGHistoryResponse
from database.models import ESGScore


# Impact weights for different action types
ACTION_IMPACT_MAP: dict[str, dict] = {
    "organic_fertilizer": {
        "environmental": 8,
        "social": 5,
        "governance": 6,
        "description": "Using organic fertilizer improves soil health and sustainability",
    },
    "chemical_fertilizer": {
        "environmental": -5,
        "social": 2,
        "governance": 3,
        "description": "Chemical fertilizer use impacts soil health negatively",
    },
    "pesticide_verified": {
        "environmental": -2,
        "social": 4,
        "governance": 8,
        "description": "Using verified pesticides shows good governance",
    },
    "pesticide_counterfeit": {
        "environmental": -10,
        "social": -8,
        "governance": -10,
        "description": "Counterfeit pesticide use is dangerous and unsustainable",
    },
    "drip_irrigation": {
        "environmental": 10,
        "social": 6,
        "governance": 7,
        "description": "Drip irrigation conserves water and improves yield",
    },
    "flood_irrigation": {
        "environmental": -4,
        "social": 2,
        "governance": 2,
        "description": "Flood irrigation wastes water resources",
    },
    "crop_rotation": {
        "environmental": 7,
        "social": 4,
        "governance": 5,
        "description": "Crop rotation maintains soil fertility naturally",
    },
    "stubble_burning": {
        "environmental": -10,
        "social": -5,
        "governance": -8,
        "description": "Stubble burning causes severe air pollution",
    },
    "composting": {
        "environmental": 9,
        "social": 5,
        "governance": 6,
        "description": "Composting recycles farm waste sustainably",
    },
    "water_harvesting": {
        "environmental": 10,
        "social": 8,
        "governance": 7,
        "description": "Rainwater harvesting is excellent for sustainability",
    },
}

# Default baseline score for new farmers
BASELINE_SCORE = 50.0


class ESGEngine:
    """Sustainability scoring engine with three-pillar assessment."""

    async def log_action(
        self, request: ESGActionRequest, db: AsyncSession
    ) -> ESGScoreResponse:
        """
        1. Look up action impact
        2. Fetch current score
        3. Calculate new scores
        4. Store and return updated ESG profile
        """
        logger.info(
            f"ESG action: {request.action_type} for farmer {request.farmer_id}"
        )

        # 1. Get impact values
        action_key = request.action_type.lower().replace(" ", "_")
        impact = ACTION_IMPACT_MAP.get(
            action_key,
            {"environmental": 0, "social": 0, "governance": 0, "description": "Unknown action"},
        )

        # 2. Fetch latest ESG score
        current = await self._get_latest_score(request.farmer_id, db)

        # 3. Calculate new scores (clamped 0-100)
        env = max(0, min(100, current["environmental"] + impact["environmental"]))
        soc = max(0, min(100, current["social"] + impact["social"]))
        gov = max(0, min(100, current["governance"] + impact["governance"]))
        overall = round((env + soc + gov) / 3, 2)

        # Determine trend
        prev_overall = current["overall"]
        if overall > prev_overall + 1:
            trend = "improving"
        elif overall < prev_overall - 1:
            trend = "declining"
        else:
            trend = "stable"

        breakdown = {
            "action": request.action_type,
            "impact": impact,
            "details": request.details,
        }

        # 4. Store new score
        new_score = ESGScore(
            farmer_id=UUID(request.farmer_id),
            score=overall,
            environmental=env,
            social=soc,
            governance=gov,
            breakdown=breakdown,
            action=request.action_type,
        )
        db.add(new_score)
        await db.flush()

        return ESGScoreResponse(
            farmer_id=request.farmer_id,
            overall_score=overall,
            environmental=env,
            social=soc,
            governance=gov,
            breakdown=breakdown,
            trend=trend,
        )

    async def get_score(
        self, farmer_id: str, db: AsyncSession
    ) -> ESGScoreResponse:
        """Get current ESG score for a farmer."""
        current = await self._get_latest_score(farmer_id, db)
        return ESGScoreResponse(
            farmer_id=farmer_id,
            overall_score=current["overall"],
            environmental=current["environmental"],
            social=current["social"],
            governance=current["governance"],
            breakdown=current.get("breakdown", {}),
        )

    async def get_history(
        self, farmer_id: str, db: AsyncSession
    ) -> ESGHistoryResponse:
        """Get ESG score history for trend analysis."""
        stmt = (
            select(ESGScore)
            .where(ESGScore.farmer_id == UUID(farmer_id))
            .order_by(ESGScore.timestamp.desc())
            .limit(50)
        )
        result = await db.execute(stmt)
        records = result.scalars().all()

        history = [
            {
                "score": r.score,
                "environmental": r.environmental,
                "social": r.social,
                "governance": r.governance,
                "action": r.action,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in records
        ]

        return ESGHistoryResponse(farmer_id=farmer_id, history=history)

    async def _get_latest_score(self, farmer_id: str, db: AsyncSession) -> dict:
        """Fetch the most recent ESG score or return baseline."""
        stmt = (
            select(ESGScore)
            .where(ESGScore.farmer_id == UUID(farmer_id))
            .order_by(ESGScore.timestamp.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        latest = result.scalar_one_or_none()

        if latest:
            return {
                "overall": latest.score,
                "environmental": latest.environmental,
                "social": latest.social,
                "governance": latest.governance,
                "breakdown": latest.breakdown or {},
            }

        return {
            "overall": BASELINE_SCORE,
            "environmental": BASELINE_SCORE,
            "social": BASELINE_SCORE,
            "governance": BASELINE_SCORE,
            "breakdown": {},
        }
