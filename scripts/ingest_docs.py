"""
Document ingestion script for the RAG Knowledge Engine.

Loads sample agricultural documents into ChromaDB for retrieval.
Run: python -m scripts.ingest_docs
"""

import uuid
from vectorstore.chroma_setup import add_documents
from app.core.logging import logger


# Sample agricultural knowledge documents
SAMPLE_DOCUMENTS = [
    {
        "content": (
            "Rice cultivation in India requires well-leveled, puddled fields with 2-5 cm standing water. "
            "Transplanting should be done 20-25 days after nursery sowing. Recommended NPK fertilizer dose "
            "is 120:60:40 kg/ha for irrigated conditions. Use zinc sulphate @ 25 kg/ha to prevent zinc deficiency. "
            "Major diseases include blast, bacterial leaf blight, and sheath blight."
        ),
        "metadata": {"source": "ICAR Rice Handbook", "page": "45", "crop": "rice"},
    },
    {
        "content": (
            "Wheat cultivation best practices: Sow between November 1-25 for optimal yield. "
            "Seed rate: 100-125 kg/ha for timely sowing. Recommended fertilizer: N:P:K = 150:60:40 kg/ha. "
            "Apply half nitrogen as basal dose, remaining in two splits. Irrigate at crown root initiation "
            "(21 DAS), tillering, jointing, flowering, and grain filling stages."
        ),
        "metadata": {"source": "IARI Wheat Guide", "page": "23", "crop": "wheat"},
    },
    {
        "content": (
            "Integrated Pest Management (IPM) for cotton: Use economic threshold levels (ETL) before spraying. "
            "American bollworm ETL: 1 larva per plant. Use pheromone traps for monitoring. "
            "Bt cotton provides resistance to bollworms. Avoid mixing insecticides unnecessarily. "
            "Use neem-based formulations as first line of defense. Rotate chemical groups to prevent resistance."
        ),
        "metadata": {"source": "CICR IPM Bulletin", "page": "12", "crop": "cotton"},
    },
    {
        "content": (
            "Organic farming certification under NPOP (National Programme for Organic Production): "
            "Conversion period is 2-3 years. Maintain buffer zones of 25 feet from conventional fields. "
            "Permitted inputs: vermicompost, neem cake, bone meal, rock phosphate. "
            "Prohibited: synthetic fertilizers, GMO seeds, sewage sludge. Maintain field records for 5 years."
        ),
        "metadata": {"source": "APEDA Organic Standards", "page": "8", "crop": "general"},
    },
    {
        "content": (
            "Drip irrigation for vegetable crops reduces water usage by 30-50% compared to flood irrigation. "
            "Emitter spacing: 30-40 cm for tomato, 40-50 cm for capsicum. Operating pressure: 1.0-1.5 kg/cm². "
            "Fertigation schedule: Apply water-soluble fertilizers 2-3 times per week. "
            "Mulching with plastic film further reduces evaporation by 20-25%."
        ),
        "metadata": {"source": "ICAR Water Management Guide", "page": "67", "crop": "vegetables"},
    },
    {
        "content": (
            "Soil Health Card scheme recommendations: Maintain soil pH between 6.5-7.5 for most crops. "
            "Organic carbon below 0.5% indicates poor soil health — add 5 tonnes FYM/ha annually. "
            "Micronutrient deficiency management: Apply ZnSO4 25 kg/ha for zinc, FeSO4 25 kg/ha for iron. "
            "Green manuring with dhaincha/sunhemp adds 20-25 kg N/ha and improves soil structure."
        ),
        "metadata": {"source": "Soil Health Card Program Manual", "page": "34", "crop": "general"},
    },
    {
        "content": (
            "Climate-resilient agriculture practices for Indian farmers: "
            "Short-duration crop varieties escape terminal drought stress. "
            "Conservation agriculture (zero/minimum tillage) improves water retention by 15-20%. "
            "System of Rice Intensification (SRI) reduces water use by 25-50% with comparable yields. "
            "Agroforestry with fruit trees provides income diversification and carbon sequestration."
        ),
        "metadata": {"source": "NICRA Project Report", "page": "89", "crop": "general"},
    },
    {
        "content": (
            "Post-harvest management for fruits and vegetables: "
            "Cool produce within 2 hours of harvest to extend shelf life. "
            "Use corrugated fiber board (CFB) boxes for transport instead of wooden crates. "
            "Mango: harvest at 80% maturity for distant markets. "
            "Tomato: ethrel treatment at 500 ppm for uniform ripening. "
            "Cold storage at 10-12°C extends tomato shelf life to 2-3 weeks."
        ),
        "metadata": {"source": "CIPHET Post-Harvest Manual", "page": "55", "crop": "horticulture"},
    },
    {
        "content": (
            "Pradhan Mantri Fasal Bima Yojana (PMFBY) crop insurance key points: "
            "Premium rates: Kharif 2%, Rabi 1.5%, Commercial/Horticultural 5%. "
            "Claim process: Report crop loss within 72 hours through app or toll-free number. "
            "Individual farm-level assessment using satellite and drone technology. "
            "Coverage includes sowing/planting risk, mid-season adversity, post-harvest losses (14 days)."
        ),
        "metadata": {"source": "PMFBY Guidelines 2024", "page": "15", "crop": "general"},
    },
    {
        "content": (
            "Pesticide safety guidelines for Indian farmers: "
            "Always read the label before use. Wear protective equipment: gloves, mask, goggles. "
            "Do not spray against wind direction. Maintain waiting period before harvest as per label. "
            "Triple-rinse empty containers and dispose at designated collection points. "
            "Never store pesticides near food, feed, or water sources. Keep away from children."
        ),
        "metadata": {"source": "CIB&RC Safety Manual", "page": "7", "crop": "general"},
    },
]


def ingest():
    """Ingest all sample documents into ChromaDB."""
    logger.info("Starting document ingestion into ChromaDB...")

    documents = [d["content"] for d in SAMPLE_DOCUMENTS]
    metadatas = [d["metadata"] for d in SAMPLE_DOCUMENTS]
    ids = [str(uuid.uuid4()) for _ in SAMPLE_DOCUMENTS]

    add_documents(documents=documents, metadatas=metadatas, ids=ids)

    logger.info(f"✅ Ingested {len(documents)} documents into ChromaDB.")


if __name__ == "__main__":
    ingest()
