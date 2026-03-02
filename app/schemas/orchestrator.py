"""
Pydantic schemas for the AI Orchestrator.
"""

from pydantic import BaseModel, Field
from typing import Any


class OrchestratorRequest(BaseModel):
    """Unified input to the orchestrator — classifies and routes."""
    farmer_id: str = Field(..., description="UUID of the farmer")
    message: str = Field(..., description="Natural language input from farmer")
    image_base64: str | None = Field(None, description="Optional attached image")
    metadata: dict = Field(default_factory=dict, description="Extra context")


class OrchestratorResponse(BaseModel):
    """Unified orchestrator response."""
    intent: str = Field(..., description="Detected intent category")
    module: str = Field(..., description="Module that handled the request")
    response: Any = Field(..., description="Module-specific response payload")
    context_summary: str | None = None
