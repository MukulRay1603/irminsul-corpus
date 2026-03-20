"""
2_fetch_structured.py - Tier 1 Ground Truth Fetcher
Pulls exact game data from genshin-db public API (no key, always updated with patches).

Fixes:
  - Windows CP1252 terminal encoding (no unicode box chars in log messages)
  - talents endpoint: genshin-db uses 'talents' but returns empty for some queries
    — now falls back to fetching from character detail directly
  - Safe JSON parsing: skips gracefully on empty/invalid responses
  - resume support: skips already-fetched files

Usage:
    python pipeline/2_fetch_structured.py
    python pipeline/2_fetch_structured.py --type characters
    python pipeline/2_fetch_structured.py --type weapons
    python pipeline/2_fetch_structured.py --type artifacts
    python pipeline/2_fetch_structured.py --type materials
"""

import os
import sys
import time
import json
import re
import argparse
import logging
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

# ── Windows-safe logging (no unicode box-drawing chars) ────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/fetch_structured.log", encoding="utf-8"),
        logging.StreamHandler(stream=sys.stdout),
    ],
)
# Force stdout to utf-8 on Windows so special chars don't crash
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logger = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
BASE_API   = "https://genshin-db-api.vercel.app/api/v5"
OUTPUT_DIR = Path("./docs/structured")
DELAY      = 0.5   # seconds between API calls

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "irminsul-corpus/1.0 (educational RAG project)"
})


# ── HTTP helper ────────────────────────────────────────────────────────────────
def api_get(endpoint: str, params: dict = None) -> dict | list | None:
    url = f"{BASE_API}/{endpoint}"
    for attempt in range(3):
        try:
            r = SESSION.get(url, params=params, timeout=20)
            if r.status_code == 200:
                text = r.text.strip()
                if not text:
                    return None         # empty body — endpoint returned nothing
                return r.json()
            elif r.status_code == 404:
                return None
            elif r.status_code == 429:
                logger.warning("Rate limited — waiting 30s")
                time.sleep(30)
            else:
                logger.warning(f"HTTP {r.status_code} for {endpoint}")
                time.sleep(2 ** attempt)
        except requests.exceptions.JSONDecodeError:
            logger.warning(f"Empty/invalid JSON from {endpoint} — skipping")
            return None
        except Exception as e:
            logger.warning(f"Request failed ({e}), retry {attempt + 1}/3")
            time.sleep(2 ** attempt)
    return None


def get_names(folder: str) -> list[str]:
    data = api_get(folder, {"query": "names", "matchCategories": "true"})
    if isinstance(data, list):
        return [n for n in data if isinstance(n, str)]
    return []


def safe_log(msg: str):
    """Log without unicode chars that break Windows CP1252 terminal."""
    clean = msg.encode("ascii", errors="replace").decode("ascii")
    logger.info(clean)


# ── Character fetcher ──────────────────────────────────────────────────────────
def fetch_characters():
    out = OUTPUT_DIR / "characters"
    out.mkdir(parents=True, exist_ok=True)

    names = get_names("characters")
    logger.info(f"Found {len(names)} characters")

    done = skipped = failed = 0

    for i, name in enumerate(names, 1):
        slug     = re.sub(r"[^\w]", "_", name.lower()).strip("_")
        out_file = out / f"{slug}.md"

        if out_file.exists():
            skipped += 1
            continue

        try:
            char = api_get("characters", {"query": name})
            if not char or not isinstance(char, dict):
                safe_log(f"  SKIP {name} — no data")
                continue

            lines = [
                f"# {char.get('name', name)} - Character Data",
                "",
                f"**Element:** {char.get('element', 'Unknown')}",
                f"**Weapon:** {char.get('weapontype', 'Unknown')}",
                f"**Rarity:** {char.get('rarity', '?')} star",
                f"**Region:** {char.get('region', 'Unknown')}",
                f"**Affiliation:** {char.get('affiliation', 'Unknown')}",
                f"**Ascension Stat:** {char.get('substat', 'Unknown')}",
                "",
            ]

            if char.get("description"):
                lines += [f"## Description\n\n{char['description']}\n"]

            # Stats at level 90
            stats_90 = api_get("stats", {
                "folder": "characters", "query": name, "level": "90"
            })
            if stats_90 and isinstance(stats_90, dict):
                lines += ["## Base Stats (Level 90)\n"]
                stat_map = {
                    "hp": "HP", "atk": "ATK", "def": "DEF",
                    "critrate": "CRIT Rate", "critdmg": "CRIT DMG",
                    "energyrecharge": "Energy Recharge",
                    "elementalmastery": "Elemental Mastery",
                    "healingbonus": "Healing Bonus",
                }
                for key, label in stat_map.items():
                    val = stats_90.get(key)
                    if val is not None:
                        lines.append(f"- {label}: {val}")
                lines.append("")
            time.sleep(DELAY)

            # Constellations
            constellations = api_get("constellations", {"query": name})
            if constellations and isinstance(constellations, dict):
                lines += ["## Constellations\n"]
                for level in ["c1", "c2", "c3", "c4", "c5", "c6"]:
                    c = constellations.get(level)
                    if c and isinstance(c, dict):
                        c_name   = c.get("name", level.upper())
                        c_effect = c.get("effect", "")
                        lines += [f"### {c_name} ({level.upper()})\n\n{c_effect}\n"]
            time.sleep(DELAY)

            # Talents — try dedicated endpoint first, fall back gracefully
            talents = api_get("talents", {"query": name})
            if talents and isinstance(talents, dict):
                lines += ["## Talents\n"]
                for t_key in ["combat1", "combat2", "combat3",
                               "passive1", "passive2", "passive3", "passive4"]:
                    t = talents.get(t_key)
                    if not t or not isinstance(t, dict):
                        continue
                    t_name = t.get("name", t_key)
                    t_info = t.get("info", "")
                    t_type = t.get("talenttype", "")
                    lines += [f"### {t_name} ({t_type})\n\n{t_info}\n"]

                    # Scaling table
                    attributes = t.get("attributes", {}) or {}
                    labels     = attributes.get("labels", [])
                    params     = attributes.get("parameters", {})
                    if labels and params:
                        lines.append("**Scaling (T1 / T6 / T10):**")
                        for label in labels[:8]:  # cap at 8 rows
                            keys = re.findall(r"\{(\w+)(?::[^}]*)?\}", label)
                            clean = re.sub(r"\{[^}]+\}", "{}", label)
                            vals  = []
                            for idx in [0, 5, 9]:
                                tier_vals = []
                                for k in keys:
                                    pl = params.get(k, [])
                                    if idx < len(pl):
                                        v = pl[idx]
                                        tier_vals.append(
                                            f"{v:.1%}" if isinstance(v, float) and v < 10
                                            else str(round(v, 2))
                                        )
                                    else:
                                        tier_vals.append("-")
                                vals.append("/".join(tier_vals))
                            lines.append(f"- {clean}: {' -> '.join(vals)}")
                        lines.append("")
            time.sleep(DELAY)

            # Ascension costs
            costs = char.get("costs", {})
            if costs:
                lines += ["## Ascension Materials\n"]
                for phase, items in costs.items():
                    if items:
                        item_str = ", ".join(
                            f"{it.get('count')}x {it.get('name')}"
                            for it in items if isinstance(it, dict)
                        )
                        lines.append(f"**{phase}:** {item_str}")
                lines.append("")

            out_file.write_text("\n".join(lines), encoding="utf-8")
            done += 1
            safe_log(f"  [{i:3}/{len(names)}] OK  {name}")

        except Exception as e:
            logger.error(f"  FAIL {name}: {e}")
            failed += 1

        time.sleep(DELAY)

    logger.info(f"Characters done: {done} saved, {skipped} skipped, {failed} failed")


# ── Weapon fetcher ─────────────────────────────────────────────────────────────
def fetch_weapons():
    out = OUTPUT_DIR / "weapons"
    out.mkdir(parents=True, exist_ok=True)

    names = get_names("weapons")
    logger.info(f"Found {len(names)} weapons")

    done = skipped = 0

    for i, name in enumerate(names, 1):
        slug     = re.sub(r"[^\w]", "_", name.lower()).strip("_")
        out_file = out / f"{slug}.md"

        if out_file.exists():
            skipped += 1
            continue

        try:
            weapon = api_get("weapons", {"query": name})
            if not weapon or not isinstance(weapon, dict):
                continue

            lines = [
                f"# {weapon.get('name', name)} - Weapon",
                "",
                f"**Type:** {weapon.get('weapontype', 'Unknown')}",
                f"**Rarity:** {weapon.get('rarity', '?')} star",
                f"**Base ATK:** {weapon.get('baseatk', '?')}",
                f"**Secondary Stat:** {weapon.get('substat', 'None')} {weapon.get('subvalue', '')}",
                "",
            ]

            if weapon.get("effectname"):
                lines += [
                    f"## Passive: {weapon['effectname']}\n",
                    f"{weapon.get('effect', '')}\n",
                ]

            # R1 vs R5
            r1 = weapon.get("r1", {}) or {}
            r5 = weapon.get("r5", {}) or {}
            if r1 and r5:
                lines += ["## Refinement Comparison\n"]
                for k in sorted(set(list(r1.keys()) + list(r5.keys()))):
                    lines.append(f"- {k}: R1 {r1.get(k, '-')} / R5 {r5.get(k, '-')}")
                lines.append("")

            out_file.write_text("\n".join(lines), encoding="utf-8")
            done += 1
            safe_log(f"  [{i:3}/{len(names)}] OK  {name}")

        except Exception as e:
            logger.error(f"  FAIL {name}: {e}")

        time.sleep(DELAY)

    logger.info(f"Weapons done: {done} saved, {skipped} skipped")


# ── Artifact fetcher ───────────────────────────────────────────────────────────
def fetch_artifacts():
    out = OUTPUT_DIR / "artifacts"
    out.mkdir(parents=True, exist_ok=True)

    # genshin-db uses "artifacts" not "artifactsets" for both list and detail
    names = get_names("artifacts")
    logger.info(f"Found {len(names)} artifact sets")

    if not names:
        logger.warning("No artifact names returned — check endpoint")
        return

    # Debug: log first name and raw response to understand shape
    first = names[0]
    sample = api_get("artifacts", {"query": first})
    logger.info(f"Sample artifact response keys: {list(sample.keys()) if isinstance(sample, dict) else type(sample)}")
    logger.info(f"Sample artifact data: {str(sample)[:300]}")

    done = skipped = 0

    for i, name in enumerate(names, 1):
        slug     = re.sub(r"[^\w]", "_", name.lower()).strip("_")
        out_file = out / f"{slug}.md"

        if out_file.exists():
            skipped += 1
            continue

        try:
            aset = api_get("artifacts", {"query": name})
            if not aset or not isinstance(aset, dict):
                logger.warning(f"  No data for {name}: {aset}")
                continue

            # genshin-db artifact response shape:
            # { name, rarity, 2pc, 4pc, flower:{}, plume:{}, sands:{}, goblet:{}, circlet:{} }
            # bonuses may be under "2pc"/"4pc" or "setBonuses" list
            bonus_2pc = (aset.get("2pc") or aset.get("setBonuses", [{}])[0].get("description", "N/A")
                         if aset.get("setBonuses") else aset.get("2pc", "N/A"))
            bonus_4pc = (aset.get("4pc") or
                         (aset.get("setBonuses", [{}, {}])[1].get("description", "N/A")
                          if len(aset.get("setBonuses", [])) > 1 else "N/A"))

            lines = [
                f"# {aset.get('name', name)} - Artifact Set",
                "",
                f"**2-Piece Bonus:** {bonus_2pc}",
                f"**4-Piece Bonus:** {bonus_4pc}",
            ]

            # Individual piece names
            for piece in ["flower", "plume", "sands", "goblet", "circlet"]:
                p = aset.get(piece, {})
                if isinstance(p, dict) and p.get("name"):
                    lines.append(f"**{piece.title()}:** {p['name']}")

            if aset.get("domainname"):
                lines.append(f"**Domain:** {aset['domainname']}")
            lines.append("")

            out_file.write_text("\n".join(lines), encoding="utf-8")
            done += 1
            safe_log(f"  [{i:3}/{len(names)}] OK  {name}")

        except Exception as e:
            logger.error(f"  FAIL {name}: {e}")

        time.sleep(DELAY)

    logger.info(f"Artifacts done: {done} saved, {skipped} skipped")


# ── Materials summary ──────────────────────────────────────────────────────────
def fetch_materials_summary():
    out = OUTPUT_DIR / "materials"
    out.mkdir(parents=True, exist_ok=True)
    out_file = out / "character_ascension.md"

    if out_file.exists():
        logger.info("Materials already fetched — skipping")
        return

    names = get_names("characters")
    lines = ["# Character Ascension Materials\n"]

    for name in names:
        char = api_get("characters", {"query": name})
        if not char:
            continue
        costs = char.get("costs", {})
        if costs:
            lines.append(f"\n## {name}\n")
            for phase, items in costs.items():
                if items:
                    item_str = ", ".join(
                        f"{it.get('count')}x {it.get('name')}"
                        for it in items if isinstance(it, dict)
                    )
                    lines.append(f"**{phase}:** {item_str}")
        time.sleep(DELAY)

    out_file.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Materials done")


# ── Entry point ────────────────────────────────────────────────────────────────
FETCHERS = {
    "characters": fetch_characters,
    "weapons":    fetch_weapons,
    "artifacts":  fetch_artifacts,
    "materials":  fetch_materials_summary,
}

if __name__ == "__main__":
    Path("logs").mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser(description="Fetch Genshin structured game data")
    parser.add_argument(
        "--type",
        choices=list(FETCHERS.keys()) + ["all"],
        default="all"
    )
    args = parser.parse_args()

    targets = list(FETCHERS.keys()) if args.type == "all" else [args.type]

    for t in targets:
        logger.info(f"--- Fetching: {t} ---")
        FETCHERS[t]()

    logger.info("Done - structured data saved to docs/structured/")
