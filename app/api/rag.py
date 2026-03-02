"""
RAG Advisory Engine API routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.rag import RAGQueryRequest, RAGResponse
from app.services.rag_service import RAGService
from database.session import get_db

router = APIRouter(prefix="/api/rag", tags=["RAG Advisory"])
_service = RAGService()


@router.post("/query", response_model=RAGResponse)
async def rag_query(request: RAGQueryRequest, db: AsyncSession = Depends(get_db)):
    """Ask the RAG advisory engine a question."""
    return await _service.query(request, db)
