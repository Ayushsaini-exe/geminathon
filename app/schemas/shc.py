"""
Pydantic schemas for Soil Health Card (SHC) integration.
"""

from pydantic import BaseModel, Field


class SHCRequest(BaseModel):
    """Request to fetch soil health card data."""
    farmer_id: str = Field(..., description="UUID of the farmer")
    shc_id: str = Field(..., description="Soil Health Card ID number")


class SoilParameters(BaseModel):
    """Parsed soil parameters from SHC."""
    nitrogen: float = Field(..., alias="N", description="Nitrogen (kg/ha)")
    phosphorus: float = Field(..., alias="P", description="Phosphorus (kg/ha)")
    potassium: float = Field(..., alias="K", description="Potassium (kg/ha)")
    ph: float = Field(..., description="Soil pH")
    organic_carbon: float = Field(..., description="Organic Carbon (%)")

    model_config = {"populate_by_name": True}


class SHCResponse(BaseModel):
    """Response with structured soil profile."""
    shc_id: str
    farmer_id: str
    soil_parameters: SoilParameters
    fertilizer_advice: str | None = None
    status: str = "success"
