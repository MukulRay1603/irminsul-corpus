"""
1_setup_tcl.py — KQM Theorycrafting Library Setup
Adds KQM/TCL as a git submodule and organises the relevant .md files
into docs/tcl/ for ingestion.

KQM TCL is the gold standard for Genshin theorycrafting:
  - Peer-reviewed by KQM Theorycrafting Editors
  - Every mechanic, ICD, reaction interaction documented with evidence
  - Hundreds of .md files, updated with every major patch
  - MIT/open license, public GitHub repo

Run ONCE to set up the submodule:
    python pipeline/1_setup_tcl.py --init

Run to refresh (pull latest TCL updates):
    python pipeline/1_setup_tcl.py --refresh

Run to re-copy files into docs/tcl/:
    python pipeline/1_setup_tcl.py --copy
"""

import os
import sys
import shutil
import subprocess
import argparse
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

TCL_REPO      = "https://github.com/KQM-git/TCL.git"
SUBMODULE_DIR = Path("./vendor/TCL")
OUTPUT_DIR    = Path("./docs/tcl")

# Which TCL directories to pull into our corpus
# Skipping evidence/ (raw test logs) and keeping the clean summary docs
TCL_INCLUDE_DIRS = [
    "docs/characters",          # per-character mechanics
    "docs/equipment",           # artifacts, weapons, food
    "docs/general-mechanics",   # ICD, gauge theory, damage formula
    "docs/combat-mechanics",    # reactions, elemental interactions
    "docs/enemy-data",          # enemy mechanics
    "docs/resources",           # glossary, team building guides
]

# Exclude raw evidence vaults — they're verbose test logs, not clean knowledge
TCL_EXCLUDE_PATTERNS = [
    "evidence/",
]


def run(cmd: list[str], cwd: str = ".") -> int:
    logger.info(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        logger.info(result.stdout.strip())
    if result.stderr:
        logger.warning(result.stderr.strip())
    return result.returncode


def init_submodule():
    """Add KQM/TCL as a git submodule."""
    if SUBMODULE_DIR.exists() and any(SUBMODULE_DIR.iterdir()):
        logger.info("TCL submodule already exists. Run --refresh to update.")
        return

    logger.info("Adding KQM/TCL as git submodule...")
    SUBMODULE_DIR.parent.mkdir(parents=True, exist_ok=True)

    ret = run(["git", "submodule", "add", "--depth", "1", TCL_REPO, str(SUBMODULE_DIR)])
    if ret != 0:
        # Fallback: shallow clone if not in a git repo
        logger.warning("git submodule failed — trying shallow clone instead")
        ret = run(["git", "clone", "--depth", "1", TCL_REPO, str(SUBMODULE_DIR)])
        if ret != 0:
            logger.error("Failed to clone TCL. Check your git installation.")
            sys.exit(1)

    logger.info("✓ TCL cloned successfully")
    copy_tcl_files()


def refresh_submodule():
    """Pull latest changes from KQM/TCL."""
    if not SUBMODULE_DIR.exists():
        logger.error("TCL not found. Run --init first.")
        sys.exit(1)

    logger.info("Pulling latest TCL changes...")
    run(["git", "pull", "origin", "master"], cwd=str(SUBMODULE_DIR))
    logger.info("✓ TCL updated")
    copy_tcl_files()


def copy_tcl_files():
    """Copy relevant TCL .md files into docs/tcl/ with clean structure."""
    if not SUBMODULE_DIR.exists():
        logger.error("TCL not found. Run --init first.")
        sys.exit(1)

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    copied = 0
    skipped = 0

    for include_dir in TCL_INCLUDE_DIRS:
        src = SUBMODULE_DIR / include_dir
        if not src.exists():
            logger.warning(f"TCL dir not found: {include_dir}")
            continue

        for md_file in src.rglob("*.md"):
            # Skip evidence vaults
            rel = md_file.relative_to(SUBMODULE_DIR)
            if any(excl in str(rel) for excl in TCL_EXCLUDE_PATTERNS):
                skipped += 1
                continue

            # Preserve directory structure under docs/tcl/
            # e.g. docs/characters/pyro/hutao.md → docs/tcl/characters/pyro/hutao.md
            rel_from_docs = md_file.relative_to(SUBMODULE_DIR / "docs")
            dest = OUTPUT_DIR / rel_from_docs
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Add source attribution header
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            header = f"<!-- Source: KQM Theorycrafting Library — {rel} -->\n<!-- License: https://github.com/KQM-git/TCL/blob/master/LICENSE -->\n\n"
            dest.write_text(header + content, encoding="utf-8")
            copied += 1

    logger.info(f"✓ Copied {copied} TCL files to {OUTPUT_DIR} ({skipped} evidence files skipped)")
    _write_tcl_index(copied)


def _write_tcl_index(count: int):
    """Write an index of all TCL files for easy reference."""
    index_lines = [
        "# KQM Theorycrafting Library Index",
        "",
        f"Total files: {count}",
        "Source: https://github.com/KQM-git/TCL",
        "License: MIT",
        "",
        "## Structure",
        "",
    ]

    for category_dir in sorted(OUTPUT_DIR.iterdir()):
        if category_dir.is_dir():
            files = list(category_dir.rglob("*.md"))
            index_lines.append(f"### {category_dir.name}/ ({len(files)} files)")
            for f in sorted(files)[:20]:  # first 20 to keep index manageable
                index_lines.append(f"- {f.relative_to(OUTPUT_DIR)}")
            if len(files) > 20:
                index_lines.append(f"- ... and {len(files) - 20} more")
            index_lines.append("")

    (OUTPUT_DIR / "INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KQM TCL submodule manager")
    parser.add_argument("--init",    action="store_true", help="Clone TCL for the first time")
    parser.add_argument("--refresh", action="store_true", help="Pull latest TCL changes")
    parser.add_argument("--copy",    action="store_true", help="Re-copy files to docs/tcl/")
    args = parser.parse_args()

    if args.init:
        init_submodule()
    elif args.refresh:
        refresh_submodule()
    elif args.copy:
        copy_tcl_files()
    else:
        # Default: init if not exists, refresh if exists
        if SUBMODULE_DIR.exists() and any(SUBMODULE_DIR.iterdir()):
            refresh_submodule()
        else:
            init_submodule()
