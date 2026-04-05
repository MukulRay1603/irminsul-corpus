# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Autonomous, self-updating Genshin Impact knowledge base for the [Irminsul RAG assistant](https://github.com/MukulRay1603/Irminsul). Runs fully automatically every week via GitHub Actions. Zero manual work after setup.

The corpus uses a **three-tier data architecture** to minimize hallucination risk:

- **Tier 1 (Ground Truth)**: `docs/tcl/` — KQM Theorycrafting Library (peer-reviewed, git submodule) + `docs/structured/` — genshin-db API (exact stats, talents, weapons, artifacts)
- **Tier 2 (Canonical)**: `docs/wiki/` — Genshin Impact Fandom Wiki via MediaWiki API
- **Tier 3 (Community)**: `docs/community/` — Reddit signals (inactive, manual only)

## Common Commands

### Pipeline Execution

```bash
# Full pipeline (all steps)
python run_pipeline.py

# Specific steps only
python run_pipeline.py --steps tcl structured
python run_pipeline.py --steps wiki
python run_pipeline.py --steps ingest

# Individual step commands
python pipeline/0_discover_characters.py      # Discover new characters from wiki
python pipeline/1_setup_tcl.py --init         # First-time TCL setup
python pipeline/1_setup_tcl.py --refresh      # Update KQM TCL
python pipeline/2_fetch_structured.py         # Fetch game data (characters, weapons, artifacts)
python pipeline/2_fetch_structured.py --type characters  # Specific data type only
python pipeline/3_scrape_wiki.py              # MediaWiki API scraper (incremental)
python pipeline/4_fetch_community.py --type all
python pipeline/4_fetch_community.py --character "Kokomi"
```

### Ingest (Pinecone)

```bash
# Ingest all docs
python ingest.py

# Single tier only
python ingest.py --dir docs/wiki

# Custom chunking
python ingest.py --chunk-size 300 --chunk-overlap 40

# Full re-index (wipes index first)
python ingest.py --clear
```

## Architecture

### Pipeline Steps (defined in `run_pipeline.py`)

0. **discover** → `pipeline/0_discover_characters.py`
   - Auto-discovers new characters from Genshin Impact Fandom Wiki
   - Compares against existing name cache
   - Writes new characters to `docs/wiki/new_characters.json`
   - Used by wiki scraper to fetch newly added characters

1. **tcl** → `pipeline/1_setup_tcl.py --refresh`
   - Pulls latest KQM Theorycrafting Library as git submodule
   - Copies relevant .md files from `vendor/TCL/docs/` to `docs/tcl/`
   - Excludes evidence vaults (raw test logs)
   - Adds source attribution headers to each file

2. **structured** → `pipeline/2_fetch_structured.py --type all`
   - Fetches from genshin-db API: `https://genshin-db-api.vercel.app/api/v5`
   - Characters: stats at level 90, talents with scaling tables, constellations, ascension costs
   - Weapons: base stats, passives, R1 vs R5 comparisons
   - Artifacts: set bonuses, piece names, domain sources
   - Outputs to `docs/structured/` as .md files
   - Resume-safe: skips already-fetched files

3. **wiki** → `pipeline/3_scrape_wiki.py`
   - Fetches from Genshin Impact Fandom Wiki via MediaWiki API
   - One .md file per character with lore, abilities, storyline
   - Incremental: skips unchanged pages (timestamp-based)
   - Smart name resolver with persistent cache
   - Outputs to `docs/wiki/characters/`

4. **community** → `pipeline/4_fetch_community.py --type all`
   - Fetches Reddit top posts (meta shifts, sentiment)
   - Tagged as "community opinion — not ground truth"
   - Best-effort step (failures don't block pipeline)

5. **ingest** → `ingest.py`
   - Embeds all .md/.txt files from `docs/` using `sentence-transformers/all-MiniLM-L6-v2` (384-dim, local, free)
   - Chunks with 300 word overlap of 40 words by default
   - Upserts to Pinecone in batches of 100
   - Requires `PINECONE_API_KEY` in environment

### GitHub Actions Workflow (`.github/workflows/update_corpus.yml`)

Runs every Sunday at 2am UTC (`cron: "0 2 * * 0"`):

1. Run pipeline steps: discover, tcl, structured, wiki
2. Commit updated metadata to repo (name_cache.json, new_characters.json, last_run.json)
3. Ingest into Pinecone (after commit, so metadata is saved even if ingest fails)
4. Upload logs as artifacts (14-day retention)

Requires GitHub Actions secrets:
- `PINECONE_API_KEY`
- `PINECONE_INDEX` (default: llmops-rag)

### Data Flow

```
KQM/TCL submodule → docs/tcl/           (peer-reviewed theorycrafting)
genshin-db API    → docs/structured/    (exact game stats)
MediaWiki API     → docs/wiki/          (canonical lore)
Reddit API        → docs/community/     (meta signals)
                    ↓
        sentence-transformers → embeddings
                    ↓
                 Pinecone      (vector DB for RAG)
```

### Key Files

- `run_pipeline.py`: Master orchestrator, defines step sequence and runs each script
- `pipeline/0_discover_characters.py`: Auto-discovers new characters from wiki
- `pipeline/1_setup_tcl.py`: Git submodule manager, copies files with attribution headers
- `pipeline/2_fetch_structured.py`: genshin-db API client with Windows CP1252 encoding fixes
- `pipeline/3_scrape_wiki.py`: MediaWiki API scraper with smart name resolution and incremental updates
- `ingest.py`: Standalone Pinecone uploader, no dependency on Irminsul serving repo

### Environment Variables

Required in `.env`:
- `PINECONE_API_KEY` — for vector DB ingest
- `PINECONE_INDEX` — index name (default: llmops-rag)

## Important Behaviors

### Windows Compatibility

`pipeline/2_fetch_structured.py` includes Windows CP1252 encoding fixes:
- Forces stdout to UTF-8 with `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`
- Uses `safe_log()` wrapper to strip unicode box chars that break Windows terminals
- Logs to both file (UTF-8) and stdout

### Resume Safety

`pipeline/2_fetch_structured.py` and `pipeline/3_scrape_wiki.py` skip already-generated files. Safe to Ctrl+C and resume without re-fetching. Wiki scraper uses timestamp-based incremental updates.

### File Exclusions

- `vendor/TCL/` is excluded from git (`.gitignore`) to avoid submodule conflicts
- Evidence vaults from KQM/TCL are excluded (verbose test logs, not clean knowledge)
- `INDEX.md` files are excluded from Pinecone ingest

## Expected Output

After full pipeline run:
- ~305 files in `docs/tcl/`
- ~405 files in `docs/structured/`
- ~130 files in `docs/wiki/characters/`
- Total: ~840 .md files
- Logs in `logs/pipeline.log`, `logs/fetch_structured.log`, `logs/wiki_scrape.log`, `logs/ingest.log`
- Metadata in `docs/wiki/name_cache.json`, `docs/wiki/new_characters.json`, `logs/last_run.json`

## Git Workflow

This repo uses:
- Git submodule for `vendor/TCL` (KQM Theorycrafting Library)
- Automated commits via GitHub Actions every Sunday
- Commit message format: `"chore: weekly corpus update YYYY-MM-DD"`
- All `docs/` changes are committed back to main branch

When working locally:
- Run `git submodule update --init --recursive` after fresh clone
- `vendor/TCL/` is ignored in `.gitignore` to prevent submodule conflicts
- GitHub Actions bot commits with user `github-actions[bot]`

## Architecture Notes

Gemini generation was replaced with deterministic MediaWiki API scraping. `generate_corpus.py` has been removed. The active pipeline is:

```
discover → tcl → structured → wiki → ingest
```

This architecture eliminates:
- LLM hallucination risk (Gemini was generating plausible but incorrect details)
- Rate limit failures (15 RPM / 1000 RPD caused GitHub Actions timeouts)
- API key dependencies (no GEMINI_API_KEY needed)

The MediaWiki API approach provides:
- Canonical lore directly from Genshin Impact Fandom Wiki
- No rate limits, no authentication required
- Incremental timestamp-based updates (only re-fetches changed pages)
- Smart name resolution with persistent caching
