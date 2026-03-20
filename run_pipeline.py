"""
run_pipeline.py — Master Pipeline Runner
Orchestrates all steps in the correct order.

Full run (weekly):
    python run_pipeline.py

Specific steps only:
    python run_pipeline.py --steps tcl structured
    python run_pipeline.py --steps synthesize
    python run_pipeline.py --steps community

Steps:
    tcl         → refresh KQM TCL submodule + copy files
    structured  → fetch genshin-db API data (characters, weapons, artifacts)
    synthesize  → Gemini prose generation grounded in Tier 1 data
    community   → Reddit community signals
    ingest      → push changed files to Pinecone
"""

import os
import sys
import time
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

STEPS = ["tcl", "structured", "synthesize", "community", "ingest"]


def run_step(script: str, args: list[str] = None) -> bool:
    cmd = [sys.executable, script] + (args or [])
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        logger.error(f"Step failed: {script} (exit {result.returncode})")
        return False
    return True


def step_tcl():
    logger.info("═══ STEP 1: KQM TCL Refresh ═══")
    return run_step("pipeline/1_setup_tcl.py", ["--refresh"])


def step_structured():
    logger.info("═══ STEP 2: Structured Data Fetch ═══")
    return run_step("pipeline/2_fetch_structured.py", ["--type", "all"])


def step_synthesize():
    logger.info("═══ STEP 3: Gemini Synthesis ═══")
    return run_step("generate_corpus.py", ["--resume"])


def step_community():
    logger.info("═══ STEP 4: Community Signals ═══")
    return run_step("pipeline/4_fetch_community.py", ["--type", "all"])


def step_ingest():
    logger.info("═══ STEP 5: Pinecone Ingest ═══")
    # Check if Irminsul path is configured
    irminsul_path = os.getenv("IRMINSUL_PATH")
    if not irminsul_path:
        logger.warning(
            "IRMINSUL_PATH not set — skipping Pinecone ingest.\n"
            "Set IRMINSUL_PATH=/path/to/irminsul in .env to enable auto-ingest."
        )
        return True  # not a failure — just skipped

    ingest_script = Path(irminsul_path) / "ingest.py"
    if not ingest_script.exists():
        logger.error(f"ingest.py not found at {ingest_script}")
        return False

    docs_path = Path("./docs").resolve()
    return run_step(
        str(ingest_script),
        ["--dir", str(docs_path), "--chunk-size", "300", "--chunk-overlap", "40"]
    )


STEP_MAP = {
    "tcl":        step_tcl,
    "structured": step_structured,
    "synthesize": step_synthesize,
    "community":  step_community,
    "ingest":     step_ingest,
}


def write_run_summary(results: dict):
    summary = {
        "run_at": datetime.now().isoformat(),
        "results": results,
        "docs_counts": {}
    }

    # Count files per tier
    for tier_dir in Path("docs").iterdir():
        if tier_dir.is_dir():
            count = sum(1 for _ in tier_dir.rglob("*.md"))
            summary["docs_counts"][tier_dir.name] = count

    Path("logs/last_run.json").write_text(
        __import__("json").dumps(summary, indent=2)
    )
    logger.info(f"Run summary: {summary['docs_counts']}")


if __name__ == "__main__":
    Path("logs").mkdir(exist_ok=True)

    parser = argparse.ArgumentParser(description="Irminsul corpus pipeline runner")
    parser.add_argument(
        "--steps",
        nargs="+",
        choices=STEPS,
        default=STEPS,
        help="Which steps to run (default: all)"
    )
    args = parser.parse_args()

    start = time.time()
    results = {}

    for step_name in args.steps:
        fn = STEP_MAP[step_name]
        ok = fn()
        results[step_name] = "ok" if ok else "failed"
        if not ok:
            logger.warning(f"Step '{step_name}' failed — continuing with remaining steps")

    elapsed = round(time.time() - start)
    logger.info(f"\n{'═'*50}")
    logger.info(f"Pipeline complete in {elapsed}s")
    for step, status in results.items():
        icon = "✓" if status == "ok" else "✗"
        logger.info(f"  {icon} {step}: {status}")
    logger.info(f"{'═'*50}")

    write_run_summary(results)
