"""
Pydantic schemas for the Digital Twin Visualization Engine.
"""

from pydantic import BaseModel, Field


class DigitalTwinUpdateRequest(BaseModel):
    """Push a risk event to the digital twin."""
    farmer_id: str = Field(..., description="UUID of the farmer")
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")
    zone_type: str = Field(..., description="disease | soil | weather | chemical")
    risk_level: str = Field("green", description="green | yellow | red")
    details: dict = Field(default_factory=dict)


class DigitalTwinZoneItem(BaseModel):
    """A single risk zone on the farm map."""
    lat: float
    lng: float
    risk_level: str
    zone_type: str
    details: dict = {}


class DigitalTwinResponse(BaseModel):
    """Full digital twin state for a farmer."""
    farmer_id: str
    zones: list[DigitalTwinZoneItem] = []
    overall_risk: str = "green"
