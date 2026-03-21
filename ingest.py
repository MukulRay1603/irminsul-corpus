"""
ingest.py — Standalone Pinecone ingest for irminsul-corpus.
No dependency on the Irminsul serving repo.

Loads all .md/.txt files from docs/, chunks them, embeds with
sentence-transformers/all-MiniLM-L6-v2 (free, local), upserts to Pinecone.

Usage:
    python ingest.py                          # ingest all of docs/
    python ingest.py --dir docs/generated     # single tier only
    python ingest.py --chunk-size 300 --chunk-overlap 40
    python ingest.py --clear                  # wipe index first, then ingest
"""

import os
import uuid
import argparse
import logging
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/ingest.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX   = os.getenv("PINECONE_INDEX", "llmops-rag")
EMBED_MODEL      = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM        = 384
BATCH_SIZE       = 100

_embedder = None

def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        logger.info(f"Loading embedder: {EMBED_MODEL}")
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedder()
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32,
        normalize_embeddings=True,
    )
    return embeddings.tolist()


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 40) -> list[str]:
    """Word-level chunker with overlap."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def load_documents(directory: str) -> list[dict]:
    """Recursively load all .md and .txt files."""
    docs = []
    for path in sorted(Path(directory).rglob("*")):
        if path.suffix in {".md", ".txt"} and path.name != "INDEX.md":
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").strip()
                if len(text) > 100:  # skip tiny/empty files
                    docs.append({"source": str(path), "text": text})
            except Exception as e:
                logger.warning(f"Could not read {path}: {e}")
    logger.info(f"Loaded {len(docs)} documents from {directory}")
    return docs


def ensure_index(pc: Pinecone):
    existing = [idx.name for idx in pc.list_indexes()]
    if PINECONE_INDEX not in existing:
        logger.info(f"Creating index '{PINECONE_INDEX}'...")
        pc.create_index(
            name=PINECONE_INDEX,
            dimension=EMBED_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        logger.info("Index created.")
    else:
        logger.info(f"Index '{PINECONE_INDEX}' already exists.")


def clear_index(pc: Pinecone):
    """Delete all vectors — use before a full re-ingest."""
    logger.info(f"Clearing all vectors from '{PINECONE_INDEX}'...")
    index = pc.Index(PINECONE_INDEX)
    index.delete(delete_all=True)
    logger.info("Index cleared.")


def ingest_documents(
    directory: str = "./docs",
    chunk_size: int = 300,
    chunk_overlap: int = 40,
    clear: bool = False,
) -> int:
    if not PINECONE_API_KEY:
        raise EnvironmentError("PINECONE_API_KEY not set in environment or .env")

    Path("logs").mkdir(exist_ok=True)

    pc = Pinecone(api_key=PINECONE_API_KEY)
    ensure_index(pc)

    if clear:
        clear_index(pc)

    index = pc.Index(PINECONE_INDEX)
    docs = load_documents(directory)

    if not docs:
        logger.warning("No documents found. Nothing ingested.")
        return 0

    # Build chunks
    all_chunks, all_meta = [], []
    for doc in docs:
        for chunk in chunk_text(doc["text"], chunk_size, chunk_overlap):
            all_chunks.append(chunk)
            all_meta.append({
                "source": doc["source"],
                "text": chunk[:1000],   # Pinecone metadata value limit
            })

    logger.info(f"Total chunks to embed: {len(all_chunks)}")

    # Embed in batches
    logger.info("Embedding chunks...")
    vectors = embed_texts(all_chunks)

    # Upsert to Pinecone in batches
    total = 0
    for i in range(0, len(all_chunks), BATCH_SIZE):
        batch = [
            (str(uuid.uuid4()), vectors[j], all_meta[j])
            for j in range(i, min(i + BATCH_SIZE, len(all_chunks)))
        ]
        index.upsert(vectors=batch)
        total += len(batch)
        logger.info(f"  Upserted {total}/{len(all_chunks)}")

    logger.info(f"Done. {total} vectors in '{PINECONE_INDEX}'.")
    return total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest corpus docs into Pinecone")
    parser.add_argument("--dir",           default="./docs",  help="Root docs directory")
    parser.add_argument("--chunk-size",    type=int, default=300)
    parser.add_argument("--chunk-overlap", type=int, default=40)
    parser.add_argument("--clear",         action="store_true",
                        help="Wipe the index before ingesting (full re-index)")
    args = parser.parse_args()

    count = ingest_documents(
        directory=args.dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        clear=args.clear,
    )
    print(f"\nIngested {count} vectors into Pinecone index '{PINECONE_INDEX}'")
