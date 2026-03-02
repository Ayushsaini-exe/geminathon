"""
Pydantic schemas for the ESG & Sustainability Scoring Engine.
"""

from pydantic import BaseModel, Field


class ESGActionRequest(BaseModel):
    """Log a new sustainability action."""
    farmer_id: str = Field(..., description="UUID of the farmer")
    action_type: str = Field(..., description="fertilizer | pesticide | water | organic")
    details: dict = Field(default_factory=dict, description="Action-specific details")


class ESGScoreResponse(BaseModel):
    """Current ESG score and breakdown."""
    farmer_id: str
    overall_score: float = Field(..., ge=0.0, le=100.0)
    environmental: float = 0.0
    social: float = 0.0
    governance: float = 0.0
    breakdown: dict = {}
    trend: str = "stable"  # improving | stable | declining


class ESGHistoryResponse(BaseModel):
    """Historical ESG scores for trend analysis."""
    farmer_id: str
    history: list[dict] = []
