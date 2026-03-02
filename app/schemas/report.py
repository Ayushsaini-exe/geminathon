"""
Pydantic schemas for the Sustainability Report Generator.
"""

from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    """Request to generate a sustainability report."""
    farmer_id: str = Field(..., description="UUID of the farmer")
    include_sections: list[str] = Field(
        default=["soil", "crops", "chemicals", "esg", "citations"],
        description="Report sections to include",
    )


class ReportResponse(BaseModel):
    """Generated report metadata."""
    farmer_id: str
    pdf_url: str | None = None
    qr_code_data: str | None = None
    report_summary: dict = {}
    status: str = "generated"
