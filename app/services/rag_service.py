"""
RAG Knowledge Engine Service.

Embeds queries, searches ChromaDB for relevant agricultural documents,
and generates structured advisory responses via Gemini.
"""

import json

from google import genai
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import logger
from app.schemas.rag import RAGQueryRequest, RAGResponse, Citation
from database.models import Farmer, ChatHistory, SoilProfile
from vectorstore.chroma_setup import query_documents


class RAGService:
    """Retrieval-Augmented Generation advisory engine."""

    def __init__(self):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-2.0-flash"

    async def query(self, request: RAGQueryRequest, db: AsyncSession) -> RAGResponse:
        """
        Full RAG pipeline:
        1. Fetch farmer profile and soil context
        2. Query ChromaDB for relevant documents
        3. Build prompt with context
        4. Generate structured response via Gemini
        5. Store chat history
        """
        logger.info(f"RAG query for farmer {request.farmer_id}: {request.question}")

        # 1. Fetch farmer context
        farmer_context = await self._get_farmer_context(request.farmer_id, db)

        # 2. Retrieve relevant documents from vector store
        rag_results = self._search_knowledge_base(request.question)

        # 3. Build prompt
        prompt = self._build_prompt(request.question, farmer_context, rag_results)

        # 4. Call Gemini and parse response
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "object",
                        "properties": {
                            "recommendation": {"type": "string"},
                            "risk_level": {"type": "string"},
                            "cost_impact": {"type": "string"},
                            "esg_impact": {"type": "string"},
                            "citations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "source": {"type": "string"},
                                        "page": {"type": "string"},
                                    },
                                },
                            },
                        },
                        "required": [
                            "recommendation",
                            "risk_level",
                            "cost_impact",
                            "esg_impact",
                        ],
                    },
                ),
            )

            raw = response.text
            if not raw or not raw.strip():
                raise ValueError("Empty response from Gemini")
            result = json.loads(raw)

        except Exception as e:
            logger.warning(f"Gemini structured call failed, trying fallback: {e}")
            try:
                fallback = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                result = {
                    "recommendation": fallback.text or "Unable to generate advice.",
                    "risk_level": "medium",
                    "cost_impact": "Consult local officer for cost details.",
                    "esg_impact": "Consult local officer for ESG details.",
                    "citations": [],
                }
            except Exception as e2:
                logger.error(f"Gemini fallback also failed: {e2}")
                result = {
                    "recommendation": f"AI advisory temporarily unavailable ({type(e).__name__}). Please try again shortly.",
                    "risk_level": "medium",
                    "cost_impact": "N/A",
                    "esg_impact": "N/A",
                    "citations": [],
                }

        # 5. Store chat history
        await self._store_chat(request.farmer_id, request.question, result, db)

        citations = [
            Citation(source=c.get("source", ""), page=c.get("page"))
            for c in result.get("citations", [])
        ]

        return RAGResponse(
            recommendation=result["recommendation"],
            risk_level=result["risk_level"],
            cost_impact=result["cost_impact"],
            esg_impact=result["esg_impact"],
            citations=citations,
            context_used=farmer_context,
        )

    async def _get_farmer_context(self, farmer_id: str, db: AsyncSession) -> dict:
        """Fetch farmer profile and recent soil data for context."""
        context = {}
        try:
            farmer = await db.get(Farmer, farmer_id)
            if farmer:
                context["name"] = farmer.name
                context["location"] = farmer.location
                context["language"] = farmer.language

            stmt = (
                select(SoilProfile)
                .where(SoilProfile.farmer_id == farmer_id)
                .order_by(SoilProfile.fetched_at.desc())
                .limit(1)
            )
            result = await db.execute(stmt)
            soil = result.scalar_one_or_none()
            if soil:
                context["soil"] = {
                    "N": soil.nitrogen,
                    "P": soil.phosphorus,
                    "K": soil.potassium,
                    "pH": soil.ph,
                    "organic_carbon": soil.organic_carbon,
                }
        except Exception as e:
            logger.warning(f"Failed to fetch farmer context: {e}")
        return context

    def _search_knowledge_base(self, question: str) -> list[dict]:
        """Search ChromaDB for relevant agricultural documents."""
        try:
            results = query_documents(query_texts=[question], n_results=5)
            documents = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    meta = {}
                    if results.get("metadatas") and results["metadatas"][0]:
                        meta = results["metadatas"][0][i]
                    documents.append({"content": doc, "metadata": meta})
            return documents
        except Exception as e:
            logger.warning(f"ChromaDB query failed: {e}")
            return []

    def _build_prompt(
        self, question: str, context: dict, rag_docs: list[dict]
    ) -> str:
        """Build the LLM prompt with farmer context and retrieved docs."""
        doc_texts = "\n\n".join(
            [
                f"[Source: {d['metadata'].get('source', 'Unknown')}]\n{d['content']}"
                for d in rag_docs
            ]
        )

        prompt = f"""You are an expert agricultural advisor and the official AI assistant for the 'AgroFix' platform used by Indian farmers.

FARMER CONTEXT:
{json.dumps(context, indent=2, default=str)}

RELEVANT KNOWLEDGE BASE DOCUMENTS:
{doc_texts if doc_texts else "No relevant documents found."}

FARMER'S QUESTION:
{question}

You handle TWO types of questions:
1. Agricultural Advisory: Answer using the KB documents and your knowledge.
2. AgroFix App Navigation & Features: If the user asks how to use the app, explain that they can use the Sidebar on the left to access:
   - Disease Scanner (upload crop photos)
   - Pesticide Verify (upload pesticide bottle photos)
   - Soil Health (sync their 12-digit SHC card)
   - Harvest Advisor (predict optimal harvesting time)
   - Sustainability (generate ESG reports for green loans)

Provide a structured JSON response with:
- recommendation: Detailed, actionable advice or app instructions.
- risk_level: one of "low", "medium", "high", "critical"
- cost_impact: Estimated financial impact and cost-saving tips (or "N/A" for app queries)
- esg_impact: Environmental and sustainability impact assessment (or "N/A" for app queries)
- citations: List of sources used (source name and page if available)

Be specific, practical, and cite the knowledge base documents when possible."""

        return prompt

    async def _store_chat(
        self, farmer_id: str, question: str, response: dict, db: AsyncSession
    ):
        """Store the Q&A exchange in chat history."""
        try:
            user_msg = ChatHistory(
                farmer_id=farmer_id,
                role="user",
                message=question,
            )
            assistant_msg = ChatHistory(
                farmer_id=farmer_id,
                role="assistant",
                message=response.get("recommendation", ""),
                context=response,
            )
            db.add(user_msg)
            db.add(assistant_msg)
            await db.flush()
        except Exception as e:
            logger.error(f"Failed to store chat history: {e}")
