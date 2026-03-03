"""
AgroFix — AI Agricultural Intelligence Platform.

Main FastAPI application with lifespan handler, CORS, and all routers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import logger
from database.session import init_db

# Import all routers
from app.api.health import router as health_router
from app.api.farmers import router as farmers_router
from app.api.rag import router as rag_router
from app.api.shc import router as shc_router
from app.api.pesticide import router as pesticide_router
from app.api.vision import router as vision_router
from app.api.harvest import router as harvest_router
from app.api.esg import router as esg_router
from app.api.digital_twin import router as digital_twin_router
from app.api.report import router as report_router
from app.api.orchestrator import router as orchestrator_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle handler."""
    logger.info("🚀 AgroFix AI Platform starting up...")

    # Initialize database tables
    await init_db()
    logger.info("✅ Database tables initialized")

    # Initialize ChromaDB
    from vectorstore.chroma_setup import get_collection
    
    # Safely handle the mocked collection if chromadb is unavailable
    collection = get_collection()
    if collection:
        try:
            doc_count = collection.count()
            logger.info(f"✅ ChromaDB ready — {doc_count} documents")
        except AttributeError:
             logger.info("⚠️ ChromaDB mocked — ready")
    else:
        logger.info("⚠️ ChromaDB disabled/unavailable")

    yield

    logger.info("🛑 AgroFix AI Platform shutting down...")


app = FastAPI(
    title="AgroFix — AI Agricultural Intelligence Platform",
    description=(
        "A comprehensive AI-powered platform for Indian farmers featuring:\n"
        "- 🌾 RAG-based crop advisory\n"
        "- 🧪 Soil Health Card integration\n"
        "- 🛡 Pesticide authenticity verification\n"
        "- 📷 AI disease detection (ResNet)\n"
        "- 📈 Harvest window optimization\n"
        "- 📊 ESG sustainability scoring\n"
        "- 🌍 Digital twin farm visualization\n"
        "- 📄 PDF report generation with QR verification"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(health_router)
app.include_router(farmers_router)
app.include_router(orchestrator_router)
app.include_router(rag_router)
app.include_router(shc_router)
app.include_router(pesticide_router)
app.include_router(vision_router)
app.include_router(harvest_router)
app.include_router(esg_router)
app.include_router(digital_twin_router)
app.include_router(report_router)


@app.get("/")
async def root():
    """Root endpoint — API info."""
    return {
        "name": "AgroFix AI Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "modules": [
            "orchestrator", "rag", "shc", "pesticide",
            "vision", "harvest", "esg", "digital_twin", "report",
        ],
    }
