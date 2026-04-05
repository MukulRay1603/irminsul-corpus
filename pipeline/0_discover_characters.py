"""
0_discover_characters.py — Auto-discover new playable characters from Genshin wiki.
Diffs wiki category against already-scraped files.
Outputs docs/wiki/new_characters.json for use by the wiki scraper.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv
load_dotenv()

# ── Logging ────────────────────────────────────────────────────────────────────
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/discover.log", encoding="utf-8"),
        logging.StreamHandler(stream=sys.stdout),
    ],
)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logger = logging.getLogger(__name__)

API_BASE = "https://genshin-impact.fandom.com/api.php"
OUTPUT_FILE = Path("docs/wiki/new_characters.json")
CHARACTERS_DIR = Path("docs/wiki/characters")

EXCLUDE = {"Traveler", "Aether", "Lumine"}

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "irminsul-corpus/1.0 (educational RAG project)"})


def safe_log(msg: str):
    clean = msg.encode("ascii", errors="replace").decode("ascii")
    logger.info(clean)


def fetch_all_playable() -> list[str]:
    """Fetch all playable character names from wiki category."""
    characters = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": "Category:Playable_Characters",
        "cmlimit": "500",
        "cmtype": "page",
        "format": "json",
    }
    while True:
        r = SESSION.get(API_BASE, params=params, timeout=20)
        data = r.json()
        members = data.get("query", {}).get("categorymembers", [])
        for m in members:
            title = m["title"]
            # Exclude subpages, files, categories, known non-playable
            if "/" in title: continue
            if ":" in title: continue
            if title in EXCLUDE: continue
            # Strip disambiguation e.g. " (Character)"
            title = title.replace(" (Character)", "").strip()
            characters.append(title)
        # Handle pagination
        if "continue" not in data:
            break
        params["cmcontinue"] = data["continue"]["cmcontinue"]
    return sorted(set(characters))


def load_scraped() -> set[str]:
    """Read 'page:' field from frontmatter of all existing scraped files."""
    scraped = set()
    for f in CHARACTERS_DIR.glob("*.md"):
        try:
            text = f.read_text(encoding="utf-8")
            for line in text.split("\n"):
                if line.startswith("page:"):
                    name = line.replace("page:", "").strip()
                    scraped.add(name)
                    break
        except Exception:
            pass
    return scraped


if __name__ == "__main__":
    safe_log("Fetching playable character list from wiki...")
    wiki_chars = fetch_all_playable()
    safe_log(f"Wiki returned: {len(wiki_chars)} playable characters")

    scraped = load_scraped()
    safe_log(f"Already scraped: {len(scraped)} characters")

    new_chars = [c for c in wiki_chars if c not in scraped]
    safe_log(f"New to fetch: {len(new_chars)}")

    if new_chars:
        safe_log("Missing characters:")
        for c in new_chars:
            safe_log(f"  - {c}")
    else:
        safe_log("Corpus up to date -- no new characters found.")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps({
        "new": new_chars,
        "all_wiki": wiki_chars,
        "total_wiki": len(wiki_chars),
        "total_scraped": len(scraped),
        "run_date": datetime.now().strftime("%Y-%m-%d"),
    }, indent=2), encoding="utf-8")

    safe_log(f"Written to {OUTPUT_FILE}")
