"""
File-based document ingestion for the RAG Knowledge Engine.

Reads .txt and .pdf files from the docs/ folder and ingests them
into ChromaDB for retrieval by the RAG advisory engine.

Usage:
    python -m scripts.ingest_files
    python -m scripts.ingest_files --dir ./my_docs
    python -m scripts.ingest_files --clear   # wipe & re-ingest
"""

import argparse
import os
import uuid
from pathlib import Path

from app.core.logging import logger


# ---------------------------------------------------------------------------
# Text extractors
# ---------------------------------------------------------------------------

def _read_txt(path: Path) -> str:
    """Read a plain-text file."""
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_pdf(path: Path) -> str:
    """Extract text from a PDF using pdfplumber (if available) or reportlab."""
    # Try pdfplumber first (best quality)
    try:
        import pdfplumber
        texts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    texts.append(text)
        return "\n\n".join(texts)
    except ImportError:
        pass

    # Fallback: PyPDF2 / pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        texts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                texts.append(text)
        return "\n\n".join(texts)
    except ImportError:
        pass

    logger.warning(
        f"Cannot read PDF '{path.name}' — install pdfplumber or pypdf: "
        "pip install pdfplumber  OR  pip install pypdf"
    )
    return ""


EXTRACTORS = {
    ".txt": _read_txt,
    ".md": _read_txt,
    ".pdf": _read_pdf,
}


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Split text into overlapping chunks for better retrieval.
    Default: ~1000 chars per chunk with 200 char overlap.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks


# ---------------------------------------------------------------------------
# Main ingestion
# ---------------------------------------------------------------------------

def ingest_directory(docs_dir: str = "./docs", clear: bool = False):
    """
    Scan docs_dir for .txt, .md, and .pdf files, chunk them,
    and add to ChromaDB.
    """
    from vectorstore.chroma_setup import get_collection, add_documents, get_chroma_client

    docs_path = Path(docs_dir)
    if not docs_path.exists():
        docs_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created docs directory: {docs_path.resolve()}")
        logger.info("Drop your .txt, .md, or .pdf files there and re-run this script.")
        return

    # Gather all supported files
    files = []
    for ext in EXTRACTORS:
        files.extend(docs_path.glob(f"*{ext}"))
        files.extend(docs_path.glob(f"**/*{ext}"))  # subdirectories too
    files = sorted(set(files))

    if not files:
        logger.warning(f"No supported files found in {docs_path.resolve()}")
        logger.info("Supported formats: .txt, .md, .pdf")
        logger.info("Drop your documents there and re-run this script.")
        return

    logger.info(f"Found {len(files)} file(s) in {docs_path.resolve()}")

    # Optionally clear existing data
    if clear:
        collection = get_collection()
        count = collection.count()
        if count > 0:
            # Delete all existing documents
            client = get_chroma_client()
            client.delete_collection("agro_knowledge")
            logger.info(f"Cleared {count} existing documents from ChromaDB")
            # Re-create the collection
            from vectorstore.chroma_setup import _collection
            import vectorstore.chroma_setup as cs
            cs._collection = None  # reset singleton

    # Extract text and chunk
    all_documents = []
    all_metadatas = []
    all_ids = []

    for filepath in files:
        ext = filepath.suffix.lower()
        extractor = EXTRACTORS.get(ext)
        if not extractor:
            continue

        logger.info(f"Processing: {filepath.name}")
        text = extractor(filepath)
        if not text or not text.strip():
            logger.warning(f"  Skipped (empty): {filepath.name}")
            continue

        chunks = _chunk_text(text)
        logger.info(f"  → {len(chunks)} chunk(s) from {filepath.name}")

        for i, chunk in enumerate(chunks):
            all_documents.append(chunk)
            all_metadatas.append({
                "source": filepath.name,
                "page": str(i + 1),
                "path": str(filepath.resolve()),
                "type": ext.lstrip("."),
            })
            all_ids.append(str(uuid.uuid4()))

    if not all_documents:
        logger.warning("No text extracted from any file.")
        return

    # Add to ChromaDB
    add_documents(
        documents=all_documents,
        metadatas=all_metadatas,
        ids=all_ids,
    )

    logger.info(f"✅ Ingested {len(all_documents)} chunks from {len(files)} file(s)")

    # Show final count
    collection = get_collection()
    logger.info(f"📊 ChromaDB total documents: {collection.count()}")


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into ChromaDB")
    parser.add_argument(
        "--dir", default="./docs",
        help="Directory containing documents (default: ./docs)",
    )
    parser.add_argument(
        "--clear", action="store_true",
        help="Clear existing ChromaDB data before ingesting",
    )
    args = parser.parse_args()
    ingest_directory(docs_dir=args.dir, clear=args.clear)


if __name__ == "__main__":
    main()
