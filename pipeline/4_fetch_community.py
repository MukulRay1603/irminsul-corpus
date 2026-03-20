"""
4_fetch_community.py — Tier 2/3 Official + Lore Fetcher
Zero auth. No Reddit. No noise.

SOURCE A — HoYoverse official (via public announcement API)
  patch notes, game notices, version updates, balance changes
  Trust: Tier 2 — directly from HoYoverse

SOURCE B — ambr.top (community-maintained lore database)
  in-game character stories, voice lines, book lore
  Trust: Tier 1 — actual in-game text

SOURCE C — torikushiii/hoyoverse-api (fan aggregator, no key)
  current events, banner history, active event calendar
  Trust: Tier 2 — mirrors official data

Usage:
    python pipeline/4_fetch_community.py
    python pipeline/4_fetch_community.py --type notices
    python pipeline/4_fetch_community.py --type events
    python pipeline/4_fetch_community.py --type banners
    python pipeline/4_fetch_community.py --type lore
    python pipeline/4_fetch_community.py --type books
    python pipeline/4_fetch_community.py --type all
"""

import re
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/fetch_community.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("./docs/community")
DELAY      = 1.2

AMBR_API   = "https://api.ambr.top/v2/en"
HOYO_ANN   = "https://sg-hk4e-api.hoyoverse.com/common/hh5bohrpg/announcement/api/getAnnList"
HOYO_CAL   = "https://api.ennead.cc/mihoyo/genshin"

HEADERS = {
    "User-Agent": "irminsul-corpus/1.0 (educational RAG; github.com/MukulRay1603/irminsul-corpus)"
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def safe_get(url: str, params: dict = None) -> dict | None:
    for attempt in range(3):
        try:
            r = SESSION.get(url, params=params, timeout=15)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                wait = 30 * (attempt + 1)
                logger.warning(f"Rate limited — waiting {wait}s")
                time.sleep(wait)
            else:
                logger.warning(f"HTTP {r.status_code} — {url}")
                return None
        except Exception as e:
            logger.warning(f"Request error: {e} (attempt {attempt+1}/3)")
            time.sleep(3 * (attempt + 1))
    return None


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def ts_to_date(ts) -> str:
    if not ts:
        return "unknown"
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return str(ts)


def file_header(title: str, source: str, trust: str) -> str:
    return "\n".join([
        f"# {title}",
        "",
        f"> **Source:** {source}",
        f"> **Trust level:** {trust}",
        f"> **Fetched:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
    ])


# ── SOURCE A: Official Notices ─────────────────────────────────────────────────
def fetch_notices():
    out = OUTPUT_DIR / "notices"
    out.mkdir(parents=True, exist_ok=True)
    logger.info("Fetching official notices...")

    data = safe_get(HOYO_ANN, params={
        "game": "hk4e", "game_biz": "hk4e_global", "lang": "en-us",
        "bundle_id": "hk4e_global", "platform": "pc",
        "region": "os_usa", "level": "55", "channel_id": "1"
    })

    if not data:
        logger.warning("Notices unavailable — skipping")
        return

    # The response nests under data.list with type_list categories
    raw = data.get("data", {}) or {}
    type_list = raw.get("type_list", [])
    all_notices = []
    for type_entry in type_list:
        all_notices.extend(type_entry.get("list", []))

    if not all_notices:
        # Fallback flat list
        all_notices = raw.get("list", [])

    if not all_notices:
        logger.warning("No notices in response")
        return

    patch_blocks = []
    notice_blocks = []

    for item in all_notices[:60]:
        title   = strip_html(item.get("title", ""))
        subtitle = strip_html(item.get("subtitle", ""))
        start   = ts_to_date(item.get("start_time"))
        banner  = item.get("banner", "")

        block = f"## {title}\n\n**Date:** {start}  \n{subtitle}\n\n---\n"

        if any(kw in title.lower() for kw in ["version", "update", "v4.", "v5.", "v6.", "patch"]):
            patch_blocks.append(block)
        else:
            notice_blocks.append(block)

    # Save patch notes
    patch_content = file_header(
        "Genshin Impact — Patch Notes & Version Updates",
        "HoYoverse official announcements",
        "Tier 2 — Official HoYoverse content"
    ) + "\n".join(patch_blocks)
    (out / "patch_notes.md").write_text(patch_content, encoding="utf-8")

    # Save general notices
    notice_content = file_header(
        "Genshin Impact — Game Notices",
        "HoYoverse official announcements",
        "Tier 2 — Official HoYoverse content"
    ) + "\n".join(notice_blocks)
    (out / "game_notices.md").write_text(notice_content, encoding="utf-8")

    logger.info(f"  ✓ {len(patch_blocks)} patch notes + {len(notice_blocks)} notices")
    time.sleep(DELAY)


# ── SOURCE C: Events + Banners ─────────────────────────────────────────────────
def fetch_events():
    out = OUTPUT_DIR / "events"
    out.mkdir(parents=True, exist_ok=True)
    logger.info("Fetching events...")

    data = safe_get(f"{HOYO_CAL}/event")
    if not data:
        logger.warning("Events unavailable — skipping")
        return

    events = data if isinstance(data, list) else \
             data.get("data", []) or data.get("events", []) or []

    lines = [file_header(
        "Genshin Impact — Current & Upcoming Events",
        "api.ennead.cc (mirrors HoYoverse official data)",
        "Tier 2 — Official event data"
    )]

    for ev in events[:40]:
        name  = strip_html(ev.get("name") or ev.get("title") or "Event")
        desc  = strip_html(ev.get("description") or ev.get("content") or "")[:500]
        start = ts_to_date(ev.get("start") or ev.get("start_time"))
        end   = ts_to_date(ev.get("end") or ev.get("end_time"))
        etype = ev.get("type") or ev.get("kind") or ""

        lines += [
            f"## {name}",
            f"**Type:** {etype}  **Duration:** {start} → {end}",
            "",
            desc,
            "",
            "---",
            "",
        ]

    (out / "current_events.md").write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"  ✓ {len(events)} events")
    time.sleep(DELAY)


def fetch_banners():
    out = OUTPUT_DIR / "banners"
    out.mkdir(parents=True, exist_ok=True)
    logger.info("Fetching banner history...")

    data = safe_get(f"{AMBR_API}/gacha")
    if not data:
        logger.warning("Banners unavailable — skipping")
        return

    banners_raw = data.get("data", {})
    banner_list = banners_raw if isinstance(banners_raw, list) else \
                  list(banners_raw.values()) if isinstance(banners_raw, dict) else []

    lines = [file_header(
        "Genshin Impact — Banner History",
        "ambr.top community database",
        "Tier 2 — Community-maintained, high accuracy"
    )]
    lines.append("Useful for: when did X character run, how many reruns, upcoming banners.\n")

    for b in banner_list[:120]:
        if not isinstance(b, dict):
            continue
        name  = b.get("name") or b.get("title") or "Banner"
        chars = b.get("r5_up_items") or b.get("fiveStarUp") or []
        ver   = b.get("version") or ""
        start = b.get("from") or b.get("begin") or b.get("start") or ""
        end   = b.get("to") or b.get("finish") or b.get("end") or ""

        if isinstance(chars, list):
            chars_str = ", ".join(
                c.get("name", str(c)) if isinstance(c, dict) else str(c)
                for c in chars
            )
        else:
            chars_str = str(chars)

        lines += [
            f"## {name} (v{ver})",
            f"**Featured 5★:** {chars_str}  **Duration:** {start} → {end}",
            "",
        ]

    (out / "banner_history.md").write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"  ✓ {len(banner_list)} banners")
    time.sleep(DELAY)


# ── SOURCE B: ambr.top Character Lore ─────────────────────────────────────────
def fetch_lore():
    out = OUTPUT_DIR / "lore"
    out.mkdir(parents=True, exist_ok=True)
    logger.info("Fetching character lore from ambr.top...")

    char_list = safe_get(f"{AMBR_API}/avatar")
    if not char_list:
        logger.warning("Character list unavailable — skipping")
        return

    characters = char_list.get("data", {}).get("items", {})
    if not characters:
        logger.warning("No characters in ambr response")
        return

    logger.info(f"  {len(characters)} characters found")

    for char_id, char_info in list(characters.items()):
        name = char_info.get("name", char_id)
        slug = name.lower().replace(" ", "_").replace("'", "").replace("-", "_")
        out_file = out / f"{slug}_lore.md"

        if out_file.exists():
            logger.info(f"  SKIP {name}")
            continue

        detail = safe_get(f"{AMBR_API}/avatar/{char_id}")
        if not detail:
            continue

        char_data = detail.get("data", {})
        fetter    = char_data.get("fetter", {}) or {}
        stories   = char_data.get("stories", []) or []
        voices    = char_data.get("voice", []) or []

        lines = [file_header(
            f"{name} — Character Stories & Lore",
            "ambr.top (official in-game character story text)",
            "Tier 1 — Canonical in-game content"
        )]

        # Profile
        for key, label in [("native", "Origin"), ("title", "Title"),
                            ("association", "Affiliation"), ("detail", "Description")]:
            val = fetter.get(key)
            if val:
                lines.append(f"**{label}:** {strip_html(val)}")
        lines.append("")

        # Stories
        if stories:
            lines.append("## Character Stories\n")
            for story in stories:
                if isinstance(story, dict):
                    t = story.get("title", "")
                    c = strip_html(story.get("text") or story.get("content") or "")
                    if t and c:
                        lines += [f"### {t}\n\n{c}\n"]

        # Voice lines (personality, lore)
        if voices:
            lines.append("## Voice Lines\n")
            for vl in voices[:25]:
                if isinstance(vl, dict):
                    vt = vl.get("title", "")
                    vc = strip_html(vl.get("text") or vl.get("content") or "")
                    if vt and vc:
                        lines.append(f"**{vt}:** {vc}\n")

        content = "\n".join(lines)
        if len(content.strip()) < 150:
            continue

        out_file.write_text(content, encoding="utf-8")
        logger.info(f"  ✓ {name}")
        time.sleep(DELAY)


# ── SOURCE B: ambr.top Book Lore ──────────────────────────────────────────────
def fetch_books():
    out = OUTPUT_DIR / "books"
    out.mkdir(parents=True, exist_ok=True)
    logger.info("Fetching in-game books from ambr.top...")

    data = safe_get(f"{AMBR_API}/book")
    if not data:
        logger.warning("Books unavailable — skipping")
        return

    books = data.get("data", {}).get("items", {})
    if not books:
        return

    all_lines = [file_header(
        "Genshin Impact — In-Game Books & Lore Texts",
        "ambr.top (official in-game collectible book text)",
        "Tier 1 — Canonical in-game content"
    )]

    for book_id, book_info in list(books.items())[:80]:
        name = book_info.get("name", book_id)
        all_lines.append(f"## {name}\n")

        detail = safe_get(f"{AMBR_API}/book/{book_id}")
        if detail:
            book_data = detail.get("data", {})
            volumes   = book_data.get("content") or book_data.get("volumes") or []
            if isinstance(volumes, list):
                for vol in volumes:
                    if isinstance(vol, dict):
                        vt = vol.get("name") or vol.get("title") or ""
                        vc = strip_html(vol.get("description") or vol.get("content") or "")
                        if vc:
                            all_lines += [f"### {vt}\n\n{vc}\n"]
            elif isinstance(volumes, str):
                all_lines.append(strip_html(volumes))

        all_lines.append("---\n")
        time.sleep(DELAY)

    (out / "ingame_books.md").write_text("\n".join(all_lines), encoding="utf-8")
    logger.info(f"  ✓ Books saved")


# ── Entry point ────────────────────────────────────────────────────────────────
FETCHERS = {
    "notices": fetch_notices,
    "events":  fetch_events,
    "banners": fetch_banners,
    "lore":    fetch_lore,
    "books":   fetch_books,
}

if __name__ == "__main__":
    Path("logs").mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser(description="Fetch Hoyolab + ambr.top official data")
    parser.add_argument("--type", choices=list(FETCHERS.keys()) + ["all"], default="all")
    args = parser.parse_args()

    targets = list(FETCHERS.keys()) if args.type == "all" else [args.type]
    for t in targets:
        logger.info(f"═══ {t} ═══")
        try:
            FETCHERS[t]()
        except Exception as e:
            logger.error(f"Failed {t}: {e}")

    logger.info("Done — saved to docs/community/")
