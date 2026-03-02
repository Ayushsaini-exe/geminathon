"""
Pydantic schemas for the RAG Advisory Engine.
"""

from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    """Request to the RAG advisory engine."""
    farmer_id: str = Field(..., description="UUID of the farmer")
    question: str = Field(..., description="Farmer's question")
    crop: str | None = Field(None, description="Current crop if relevant")
    location: str | None = Field(None, description="Location override")


class Citation(BaseModel):
    """A source citation from the knowledge base."""
    source: str
    page: str | None = None
    relevance_score: float | None = None


class RAGResponse(BaseModel):
    """Structured response from the RAG advisory engine."""
    recommendation: str
    risk_level: str = Field(..., description="low | medium | high | critical")
    cost_impact: str
    esg_impact: str
    citations: list[Citation] = []
    context_used: dict | None = None
