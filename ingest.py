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
import re
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


def extract_metadata(filepath: Path) -> dict:
    """
    Extract rich metadata from a document filepath and frontmatter.
    Used to populate Pinecone vector metadata for smart filtering.
    """
    path_str = str(filepath).replace("\\", "/")
    parts = filepath.parts

    # Determine tier from path
    tier = "unknown"
    if "docs/tcl" in path_str or "docs\\tcl" in path_str:
        tier = "tcl"
    elif "docs/structured" in path_str or "docs\\structured" in path_str:
        tier = "structured"
    elif "docs/wiki" in path_str or "docs\\wiki" in path_str:
        tier = "wiki"
    elif "docs/community" in path_str or "docs\\community" in path_str:
        tier = "community"

    # Determine content_type from subfolder
    content_type = "general"
    if "/characters/" in path_str or "\\characters\\" in path_str:
        content_type = "character"
    elif "/weapons/" in path_str or "\\weapons\\" in path_str:
        content_type = "weapon"
    elif "/artifacts/" in path_str or "\\artifacts\\" in path_str:
        content_type = "artifact"
    elif "/reactions/" in path_str or "\\reactions\\" in path_str:
        content_type = "reaction"
    elif "/mechanics/" in path_str or "\\mechanics\\" in path_str:
        content_type = "mechanic"
    elif "/nations/" in path_str or "\\nations\\" in path_str:
        content_type = "nation"
    elif "/lore/" in path_str or "\\lore\\" in path_str:
        content_type = "lore"

    # Extract character name from filename for character files
    character = ""
    if content_type == "character":
        stem = filepath.stem  # e.g. "hu_tao", "traveler_anemo"
        character = stem.replace("_", " ").title()
        # Skip template/index files
        if character.lower().startswith((' template', 'template', 'index', 'readme')):
            character = ""

    # Tier trust score for ranking
    trust = {"tcl": 1.0, "structured": 1.0, "wiki": 0.8,
             "community": 0.5, "unknown": 0.3}.get(tier, 0.3)

    return {
        "tier": tier,
        "content_type": content_type,
        "character": character,
        "trust_score": trust,
        "source_file": filepath.name,
    }


def clean_document_text(text: str) -> str:
    """
    Strip frontmatter, wiki notices, HTML comments,
    and other noise before chunking.
    """
    # Strip YAML frontmatter (--- ... ---)
    text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', text,
                  flags=re.DOTALL)

    # Strip HTML comments <!-- ... -->
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    # Strip wiki "page being created" notices
    # These appear as short paragraphs with words like:
    # "currently being created", "Join the Discord"
    lines = text.split('\n')
    clean_lines = []
    skip_patterns = [
        'currently being created',
        'currently being expanded',
        'currently being restructured',
        'join the',
        'discord',
        'leave a message',
        'contact the editor',
        'user walls',
        'last edit:',
        'if this was over two weeks',
        'before removing the tag',
        'import char from',
        'import skillicon',
        'import image from',
        '@site/src/',
        '@theme/',
        'this page is currently',
        '(utc)',
        'ago). if',
        'funds',  # wiki editor usernames that slip through
    ]
    for line in lines:
        # Skip lines with text matching patterns
        if any(p in line.lower() for p in skip_patterns):
            continue
        # Skip lines that look like "X weeks/months/days ago"
        if re.search(r'\d+\s+(week|month|day|hour)s?\s+ago', line.lower()):
            continue
        # Skip very short isolated lines (< 4 chars, likely wiki artifacts)
        # But keep lines that are part of headers (start with #)
        if len(line.strip()) < 4 and not line.strip().startswith('#'):
            continue
        clean_lines.append(line)
    text = '\n'.join(clean_lines)

    # Collapse 3+ blank lines to 2
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def section_aware_chunk(text: str, chunk_size: int = 300,
                         overlap: int = 40) -> list[dict]:
    """
    Split document into chunks that respect ## section boundaries.
    Each chunk knows which section it came from.
    Returns list of dicts: {"text": str, "section": str}
    """
    # Split by ## headers (keep headers with their content)
    section_pattern = re.compile(r'^(#{1,3}\s+.+)$', re.MULTILINE)
    parts = section_pattern.split(text)

    # Pair headers with their content
    sections = []
    current_header = "Introduction"

    for i, part in enumerate(parts):
        if section_pattern.match(part.strip()):
            current_header = part.strip().lstrip('#').strip()
        else:
            if part.strip():
                sections.append({
                    "header": current_header,
                    "content": part.strip()
                })

    # Now chunk each section's content
    chunks = []
    for section in sections:
        words = section["content"].split()
        if not words:
            continue
        i = 0
        while i < len(words):
            chunk_words = words[i: i + chunk_size]
            chunk_text = " ".join(chunk_words)
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "section": section["header"]
                })
            i += chunk_size - overlap

    # If no sections found, fall back to word chunking
    if not chunks:
        words = text.split()
        i = 0
        while i < len(words):
            chunk_words = words[i: i + chunk_size]
            chunk_text = " ".join(chunk_words)
            if chunk_text.strip():
                chunks.append({"text": chunk_text, "section": "General"})
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

    # Build chunks with smart metadata
    all_chunks = []   # list of text strings for embedding
    all_meta = []     # list of metadata dicts for Pinecone

    for doc in docs:
        filepath = Path(doc["source"])
        file_meta = extract_metadata(filepath)
        cleaned_text = clean_document_text(doc["text"])

        chunk_dicts = section_aware_chunk(
            cleaned_text, chunk_size, chunk_overlap
        )

        for chunk_dict in chunk_dicts:
            chunk_text_val = chunk_dict["text"]
            section = chunk_dict["section"]

            # Detect section-level content type
            section_lower = section.lower()
            section_content_type = file_meta["content_type"]
            if any(w in section_lower for w in
                   ["constellation", "passive", "talent", "skill", "burst"]):
                section_content_type = "ability"
            elif any(w in section_lower for w in
                     ["lore", "story", "personality", "appearance", "history"]):
                section_content_type = "lore"
            elif any(w in section_lower for w in
                     ["build", "weapon", "artifact", "team", "rotation", "bis"]):
                section_content_type = "build"
            elif any(w in section_lower for w in
                     ["stat", "scaling", "ascension", "material"]):
                section_content_type = "stats"

            all_chunks.append(chunk_text_val)
            all_meta.append({
                # Keep existing fields
                "source": doc["source"],
                "text": chunk_text_val[:1000],
                # New smart metadata
                "tier": file_meta["tier"],
                "content_type": section_content_type,
                "character": file_meta["character"],
                "section": section[:100],
                "trust_score": file_meta["trust_score"],
                "source_file": file_meta["source_file"],
            })

    logger.info(f"Total chunks to embed: {len(all_chunks)}")

    # Embed in batches
    logger.info("Embedding chunks...")
    vectors = embed_texts(all_chunks)

    # Upsert to Pinecone in batches
    total = 0
    for i in range(0, len(all_chunks), BATCH_SIZE):
        batch = []
        for j in range(i, min(i + BATCH_SIZE, len(all_chunks))):
            batch.append({
                "id": str(uuid.uuid4()),
                "values": vectors[j],
                "metadata": all_meta[j],
            })
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
