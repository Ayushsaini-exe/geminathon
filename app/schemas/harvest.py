"""
Pydantic schemas for the Harvest Window Arbitrage Engine.
"""

from pydantic import BaseModel, Field


class HarvestRequest(BaseModel):
    """Request for harvest window analysis."""
    farmer_id: str = Field(..., description="UUID of the farmer")
    crop: str = Field(..., description="Crop name")
    location: str = Field(..., description="Location for weather/market data")
    current_maturity_pct: float = Field(80.0, description="Crop maturity percentage")


class HarvestScenarioItem(BaseModel):
    """One simulated harvest scenario."""
    label: str  # e.g., "Harvest Today", "Harvest +2 Days"
    harvest_day: str
    weather_risk: str  # low | medium | high
    mandi_price_per_quintal: float
    transport_cost: float
    estimated_yield_quintal: float
    net_profit: float
    quality_loss_pct: float = 0.0


class HarvestResponse(BaseModel):
    """Response with scenario comparison and recommendation."""
    crop: str
    scenarios: list[HarvestScenarioItem]
    recommendation: str
    recommended_scenario: str
