"""
3_scrape_wiki.py — Tier 2 Wiki Scraper (MediaWiki API)
Pulls canonical lore from Genshin Impact Fandom Wiki.

Replaces generate_corpus.py (Gemini LLM generation) with deterministic scraping.
Zero hallucination risk, no rate limits, canonical lore auto-updating weekly.

Usage:
    python pipeline/3_scrape_wiki.py                    # all characters
    python pipeline/3_scrape_wiki.py --character "Hu Tao"
    python pipeline/3_scrape_wiki.py --clear             # wipe and redo all
"""

import os
import sys
import time
import json
import re
import argparse
import logging
from pathlib import Path
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# ── Windows-safe logging (no unicode box-drawing chars) ────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/wiki_scrape.log", encoding="utf-8"),
        logging.StreamHandler(stream=sys.stdout),
    ],
)
# Force stdout to utf-8 on Windows so special chars don't crash
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logger = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
API_BASE   = "https://genshin-impact.fandom.com/api.php"
OUTPUT_DIR = Path("./docs/wiki/characters")
NAME_CACHE_FILE = Path("./docs/wiki/name_cache.json")
DELAY      = 1.5   # seconds between API calls (be polite, parse endpoint is heavier)

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "irminsul-corpus/1.0 (educational RAG project)"
})

# Subpages to fetch per character (in order)
# /Lore is always a redirect to /Profile, so skip it
SUBPAGES = ["/Storyline", "/Profile"]

# Traveler element variants
TRAVELER_ELEMENTS = ["Anemo", "Electro", "Geo", "Hydro", "Pyro", "Cryo", "Dendro"]

# Character list to scrape (hardcoded for now)
CHARACTERS = [
    "Hu Tao", "Zhongli", "Kazuha", "Xiao", "Neuvillette", "Furina",
    "Raiden Shogun", "Nahida", "Ayaka", "Bennett", "Xiangling", "Xingqiu",
    "Yelan", "Fischl", "Ganyu", "Venti", "Yae Miko", "Arlecchino", "Navia",
    "Wriothesley", "Cyno", "Tighnari", "Baizhu", "Kokomi", "Albedo", "Shenhe",
    "Rosaria", "Beidou", "Keqing", "Sucrose", "Barbara", "Lyney", "Wanderer",
    "Itto", "Dehya", "Yoimiya", "Clorinde", "Sigewinne", "Kinich", "Xilonen",
    "Mavuika",
    # New additions
    "Varka", "Skirk", "Escoffier", "Citlali", "Chasca", "Ororon", "Emilie",
    "Sethos", "Chevreuse", "Chiori", "Gaming", "Linnea", "Lauma", "Nefer",
    "Varesa"
]

# Sections to skip (filter out after cleanup)
SKIP_SECTIONS = {
    "Trivia", "Other Languages", "Gallery", "Navigation",
    "Voice-Overs", "Version History", "Availability", "Etymology",
    "Notes", "References", "Change History"
}


def safe_log(msg: str):
    """Log without unicode chars that break Windows CP1252 terminal."""
    clean = msg.encode("ascii", errors="replace").decode("ascii")
    logger.info(clean)


# ── Name Cache Management ──────────────────────────────────────────────────────
def load_name_cache() -> dict:
    """Load name resolution cache from disk."""
    if NAME_CACHE_FILE.exists():
        try:
            return json.loads(NAME_CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_name_cache(cache: dict):
    """Save name resolution cache to disk."""
    NAME_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    NAME_CACHE_FILE.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")


# ── API helpers ────────────────────────────────────────────────────────────────
def api_get(params: dict) -> dict | None:
    """Call MediaWiki API with retry logic."""
    for attempt in range(3):
        try:
            r = SESSION.get(API_BASE, params=params, timeout=20)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 404:
                return None
            elif r.status_code == 429:
                logger.warning("Rate limited — waiting 30s")
                time.sleep(30)
            else:
                logger.warning(f"HTTP {r.status_code}")
                time.sleep(2 ** attempt)
        except Exception as e:
            logger.warning(f"Request failed ({e}), retry {attempt + 1}/3")
            time.sleep(2 ** attempt)
    return None


def resolve_wiki_name(character: str) -> str | None:
    """
    Resolve character display name to wiki page name.
    Uses caching and MediaWiki search API for auto-discovery.
    """
    cache = load_name_cache()

    # Check cache first
    if character in cache:
        return cache[character]

    # Try name as-is (spaces → underscores)
    candidate = character.replace(" ", "_")

    # Test if this page exists by trying to fetch it
    params = {
        "action": "query",
        "titles": candidate,
        "format": "json",
    }
    data = api_get(params)
    if data:
        pages = data.get("query", {}).get("pages", {})
        page_data = list(pages.values())[0] if pages else {}
        if "missing" not in page_data and "invalid" not in page_data:
            # Page exists! Cache and return
            cache[character] = candidate
            save_name_cache(cache)
            return candidate

    # Try MediaWiki search API
    params = {
        "action": "query",
        "list": "search",
        "srsearch": character,
        "srnamespace": "0",
        "srlimit": "3",
        "format": "json",
    }
    data = api_get(params)
    if data:
        results = data.get("query", {}).get("search", [])
        # Find first result where all character name words appear in title
        char_words = set(character.lower().split())
        for result in results:
            title = result["title"]
            title_lower = title.lower()
            if all(word in title_lower for word in char_words):
                wiki_name = title.replace(" ", "_")
                cache[character] = wiki_name
                save_name_cache(cache)
                safe_log(f"  Resolved '{character}' → '{wiki_name}' via search")
                return wiki_name

    # Nothing worked
    logger.warning(f"  Could not resolve wiki name for: {character}")
    return None


def get_page_last_modified(page_name: str) -> str | None:
    """Get the last modification timestamp of a wiki page."""
    params = {
        "action": "query",
        "titles": page_name,
        "prop": "revisions",
        "rvprop": "timestamp",
        "rvlimit": "1",
        "format": "json",
    }
    data = api_get(params)
    if not data:
        return None

    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return None

    page_data = list(pages.values())[0]
    if "missing" in page_data or "invalid" in page_data:
        return None

    revisions = page_data.get("revisions", [])
    if not revisions:
        return None

    return revisions[0].get("timestamp", None)


def fetch_rendered(page: str) -> str | None:
    """Fetch rendered HTML for a wiki page, then strip to plain text."""
    params = {
        "action": "parse",
        "page": page,
        "prop": "text",
        "format": "json",
        "disablelimitreport": "1",
        "disableeditsection": "1",
    }
    data = api_get(params)
    if not data:
        return None

    # Check for errors (page doesn't exist)
    if "error" in data:
        error_code = data.get("error", {}).get("code", "")
        if error_code == "missingtitle":
            return None
        logger.warning(f"API error: {data.get('error', {}).get('info', 'unknown')}")
        return None

    # Check if parse key exists
    if "parse" not in data:
        return None

    # Get rendered HTML
    html = data.get("parse", {}).get("text", {}).get("*", "")
    if not html:
        return None

    # Strip HTML to plain text using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Remove these tags AND their contents entirely
    for tag in soup.find_all(["table", "script", "style", "sup",
                               "nav", "aside", "figure"]):
        tag.decompose()

    # Remove by class name
    for elem in soup.find_all(class_=["toc", "mw-editsection", "reference"]):
        elem.decompose()

    # Remove wiki navigation tabs and UI elements
    for elem in soup.find_all(class_=["pi-navigation", "wds-tabs",
                                       "wds-tabs__tab", "page-header",
                                       "portable-infobox", "pi-item",
                                       "custom-tabs", "custom-tabs-default"]):
        elem.decompose()

    # Remove any div with id="toc" (table of contents)
    toc = soup.find(id="toc")
    if toc:
        toc.decompose()

    # Convert to text preserving line breaks
    text = soup.get_text(separator="\n", strip=True)

    return text


# ── Wikitext cleanup ───────────────────────────────────────────────────────────
def clean_wikitext(wikitext: str) -> str:
    """Strip wikitext markup → clean markdown."""
    if not wikitext:
        return ""

    text = wikitext

    # Remove templates: {{anything}}
    # Handle nested templates with multiple passes
    for _ in range(5):
        text = re.sub(r'\{\{[^{}]*\}\}', '', text)

    # Remove remaining template artifacts
    text = re.sub(r'\{\{.*?\}\}', '', text, flags=re.DOTALL)

    # Remove file/image references
    text = re.sub(r'\[\[File:.*?\]\]', '', text, flags=re.DOTALL)
    text = re.sub(r'\[\[Image:.*?\]\]', '', text, flags=re.DOTALL)

    # Remove gallery tags
    text = re.sub(r'<gallery[^>]*>.*?</gallery>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Remove reference tags
    text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<ref[^>]*/>', '', text, flags=re.IGNORECASE)

    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    # Remove other HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove categories
    text = re.sub(r'\[\[Category:.*?\]\]', '', text, flags=re.IGNORECASE)

    # Convert wikilinks to plain text: [[Link|Display]] → Display, [[Link]] → Link
    text = re.sub(r'\[\[(?:[^|\]]+\|)?([^\]]+)\]\]', r'\1', text)

    # Convert headers: == Header == → ## Header
    text = re.sub(r'^====\s*(.*?)\s*====\s*$', r'#### \1', text, flags=re.MULTILINE)
    text = re.sub(r'^===\s*(.*?)\s*===\s*$', r'### \1', text, flags=re.MULTILINE)
    text = re.sub(r'^==\s*(.*?)\s*==\s*$', r'## \1', text, flags=re.MULTILINE)

    # Convert bold/italic: '''bold''' → **bold**, ''italic'' → *italic*
    text = re.sub(r"'''(.*?)'''", r'**\1**', text)
    text = re.sub(r"''(.*?)''", r'*\1*', text)

    # Clean up HTML entities
    text = text.replace('&mdash;', '—')
    text = text.replace('&ndash;', '–')
    text = text.replace('&amp;', '&')
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")

    # Clean up multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove lines that are just whitespace
    lines = [line.rstrip() for line in text.split('\n')]
    text = '\n'.join(lines)

    return text.strip()


def filter_sections(text: str) -> str:
    """Remove unwanted sections from cleaned markdown text."""
    if not text:
        return ""

    # Split by ## headers
    sections = re.split(r'\n(##\s+.+)\n', text)

    # sections now looks like: [intro_text, '## Section1', section1_content, '## Section2', section2_content, ...]
    # We need to filter out sections whose title is in SKIP_SECTIONS

    filtered = []
    i = 0

    # Handle text before first section (if any)
    if sections and not sections[0].startswith('##'):
        filtered.append(sections[0])
        i = 1

    # Process sections in pairs: header + content
    while i < len(sections) - 1:
        header = sections[i]
        content = sections[i + 1] if i + 1 < len(sections) else ""

        # Extract section title from header
        title_match = re.match(r'##\s+(.+)', header)
        if title_match:
            title = title_match.group(1).strip()
            # Keep section if title not in SKIP_SECTIONS
            if title not in SKIP_SECTIONS:
                filtered.append(header)
                filtered.append(content)

        i += 2

    return '\n'.join(filtered).strip()


# ── Character fetcher ──────────────────────────────────────────────────────────
def fetch_character(character: str) -> bool:
    """Fetch wiki data for one character."""
    # Special handling for Traveler variants
    if character == "Traveler":
        return fetch_traveler_variants()

    slug = re.sub(r"[^\w]", "_", character.lower()).strip("_")
    slug = re.sub(r"_+", "_", slug)  # collapse multiple underscores
    out_file = OUTPUT_DIR / f"{slug}.md"

    # Resolve wiki name
    wiki_name = resolve_wiki_name(character)
    if not wiki_name:
        logger.error(f"  FAIL {character} — could not resolve wiki name")
        return False

    # Check if we need to update existing file
    if out_file.exists() and out_file.stat().st_size > 200:
        # Read scraped date from frontmatter
        try:
            existing_text = out_file.read_text(encoding="utf-8")
            scraped_date = None
            for line in existing_text.split("\n"):
                if line.startswith("scraped:"):
                    scraped_date = line.replace("scraped:", "").strip()
                    break

            if scraped_date:
                # Check if any subpage was modified after scraped date
                needs_update = False
                for subpage in SUBPAGES:
                    page_name = f"{wiki_name}{subpage}"
                    last_modified = get_page_last_modified(page_name)
                    if last_modified:
                        # Compare timestamps (ISO format is directly comparable)
                        if last_modified[:10] > scraped_date:
                            needs_update = True
                            safe_log(f"  UPDATE needed — {subpage.strip('/')} modified {last_modified[:10]}")
                            break

                if not needs_update:
                    safe_log(f"  SKIP {character} — up to date (scraped {scraped_date})")
                    return True
                else:
                    safe_log(f"  UPDATING {character} — wiki changed since {scraped_date}")
        except Exception as e:
            logger.warning(f"  Could not check update status: {e}, will re-fetch")

    fetched_subpages = []
    content_sections = []

    # Try fetching each subpage
    for subpage in SUBPAGES:
        page_name = f"{wiki_name}{subpage}"
        subpage_title = subpage.strip("/")  # Define before if/else to avoid scoping error
        safe_log(f"  Fetching {page_name}...")

        rendered = fetch_rendered(page_name)
        if rendered:
            cleaned = clean_wikitext(rendered)
            filtered = filter_sections(cleaned)

            # Fallback: if filtering removed too much content, use unfiltered
            if filtered and len(filtered) < 300 and len(cleaned) > 300:
                safe_log(f"    Filtering too aggressive — using unfiltered content")
                filtered = cleaned

            if filtered and len(filtered) > 100:
                content_sections.append(f"## {subpage_title}\n\n{filtered}")
                fetched_subpages.append(subpage_title)
                safe_log(f"    OK {subpage_title}: {len(filtered)} chars")
            else:
                safe_log(f"    SKIP {subpage_title} — empty after cleanup")
        else:
            safe_log(f"    -- {subpage_title} not found")

        time.sleep(DELAY)

    # Fallback: if no subpages found, try main page
    if not content_sections:
        logger.warning(f"  No subpages found for {character} — trying main page")
        main_rendered = fetch_rendered(wiki_name)
        if main_rendered:
            cleaned = clean_wikitext(main_rendered)
            filtered = filter_sections(cleaned)

            # Fallback: if filtering removed too much content, use unfiltered
            if filtered and len(filtered) < 300 and len(cleaned) > 300:
                safe_log(f"    Filtering too aggressive — using unfiltered content")
                filtered = cleaned

            if filtered and len(filtered) > 100:
                content_sections.append(f"## Overview\n\n{filtered}")
                fetched_subpages.append("Main page")
                safe_log(f"    OK Main page: {len(filtered)} chars")
        time.sleep(DELAY)

    # If still nothing, fail gracefully
    if not content_sections:
        logger.error(f"  FAIL {character} — no content found")
        return False

    # Build output file
    frontmatter = "\n".join([
        "---",
        "source: genshin-impact.fandom.com",
        f"page: {character}",
        f"subpages: {', '.join(fetched_subpages)}",
        f"scraped: {datetime.now().strftime('%Y-%m-%d')}",
        "tier: wiki",
        "---",
        "",
    ])

    full_content = frontmatter + f"# {character}\n\n" + "\n\n".join(content_sections)

    out_file.write_text(full_content, encoding="utf-8")
    safe_log(f"  OK {character} — saved {len(full_content)} chars")
    return True


def fetch_traveler_variants() -> bool:
    """Fetch all Traveler element variants."""
    safe_log("  Fetching Traveler variants...")
    success_count = 0

    for element in TRAVELER_ELEMENTS:
        safe_log(f"  [{element}] Fetching Traveler ({element})...")

        slug = f"traveler_{element.lower()}"
        out_file = OUTPUT_DIR / f"{slug}.md"

        fetched_subpages = []
        content_sections = []

        # Try subpages first: "Traveler (Element)/Storyline" and "Traveler (Element)/Profile"
        for subpage in SUBPAGES:
            page_name = f"Traveler ({element}){subpage}"
            subpage_title = subpage.strip("/")
            safe_log(f"    Fetching {page_name}...")

            rendered = fetch_rendered(page_name)
            if rendered:
                cleaned = clean_wikitext(rendered)
                filtered = filter_sections(cleaned)

                if filtered and len(filtered) < 300 and len(cleaned) > 300:
                    filtered = cleaned

                if filtered and len(filtered) > 100:
                    content_sections.append(f"## {subpage_title}\n\n{filtered}")
                    fetched_subpages.append(subpage_title)
                    safe_log(f"      OK {subpage_title}: {len(filtered)} chars")
            else:
                safe_log(f"      -- {subpage_title} not found")

            time.sleep(DELAY)

        # Fallback: if no subpages found, try main page "Traveler (Element)"
        if not content_sections:
            safe_log(f"    No subpages found — trying main page")
            main_page = f"Traveler ({element})"
            rendered = fetch_rendered(main_page)
            if rendered:
                cleaned = clean_wikitext(rendered)
                filtered = filter_sections(cleaned)

                if filtered and len(filtered) < 300 and len(cleaned) > 300:
                    filtered = cleaned

                if filtered and len(filtered) > 100:
                    content_sections.append(f"## Overview\n\n{filtered}")
                    fetched_subpages.append("Main page")
                    safe_log(f"      OK Main page: {len(filtered)} chars")
            time.sleep(DELAY)

        if content_sections:
            # Build output file for this element
            frontmatter = "\n".join([
                "---",
                "source: genshin-impact.fandom.com",
                f"page: Traveler ({element})",
                f"subpages: {', '.join(fetched_subpages)}",
                f"scraped: {datetime.now().strftime('%Y-%m-%d')}",
                "tier: wiki",
                "---",
                "",
            ])

            full_content = frontmatter + f"# Traveler ({element})\n\n" + "\n\n".join(content_sections)
            out_file.write_text(full_content, encoding="utf-8")
            safe_log(f"  OK Traveler ({element}) — saved {len(full_content)} chars")
            success_count += 1
        else:
            safe_log(f"  SKIP Traveler ({element}) — no content found")

    return success_count > 0


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    Path("logs").mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser(description="Scrape Genshin wiki lore via MediaWiki API")
    parser.add_argument(
        "--character",
        type=str,
        default=None,
        help="Single character to scrape (e.g., 'Hu Tao')"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Wipe docs/wiki/characters/ before starting"
    )
    args = parser.parse_args()

    if args.clear:
        logger.info("Clearing existing wiki files...")
        for f in OUTPUT_DIR.glob("*.md"):
            f.unlink()
        logger.info("Cleared.")

    if args.character:
        targets = [args.character]
    else:
        # Start with hardcoded list
        targets = list(CHARACTERS)

        # Add new characters from discovery
        new_chars_file = Path("docs/wiki/new_characters.json")
        if new_chars_file.exists():
            import json
            data = json.loads(new_chars_file.read_text(encoding="utf-8"))
            new_list = data.get("new", [])
            if new_list:
                logger.info(f"Found {len(new_list)} new characters from discovery")
                targets.extend(new_list)
                # Deduplicate while preserving order
                seen = set()
                targets = [x for x in targets if not (x in seen or seen.add(x))]

    total = len(targets)

    logger.info(f"Scraping wiki data for {total} character(s)")
    logger.info("=" * 60)

    done = 0
    failed = []

    for i, character in enumerate(targets, 1):
        logger.info(f"[{i:3}/{total}] {character}")
        try:
            ok = fetch_character(character)
            if ok:
                done += 1
            else:
                failed.append(character)
        except Exception as e:
            logger.error(f"  ERROR {character}: {e}")
            failed.append(character)

    logger.info("=" * 60)
    logger.info(f"Done: {done}/{total} characters scraped")
    if failed:
        logger.info(f"Failed: {failed}")
    logger.info(f"Output: {OUTPUT_DIR}")
