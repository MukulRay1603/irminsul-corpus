# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Autonomous, self-updating Genshin Impact knowledge base for the [Irminsul RAG assistant](https://github.com/MukulRay1603/Irminsul). Runs fully automatically every week via GitHub Actions. Zero manual work after setup.

The corpus uses a **three-tier data architecture** to minimize hallucination risk:

- **Tier 1 (Ground Truth)**: `docs/tcl/` — KQM Theorycrafting Library (peer-reviewed, git submodule) + `docs/structured/` — genshin-db API (exact stats, talents, weapons, artifacts)
- **Tier 2 (Expert Synthesis)**: `docs/generated/` — Gemini writes WITH Tier 1 data as context (cannot hallucinate stats because the numbers are in the prompt)
- **Tier 3 (Community Signal)**: `docs/community/` — Reddit top posts (meta shifts, buff/nerf sentiment, explicitly tagged as opinion)

## Common Commands

### Pipeline Execution

```bash
# Full pipeline (all steps)
python run_pipeline.py

# Specific steps only
python run_pipeline.py --steps tcl structured
python run_pipeline.py --steps synthesize
python run_pipeline.py --steps ingest

# Individual step commands
python pipeline/1_setup_tcl.py --init         # First-time TCL setup
python pipeline/1_setup_tcl.py --refresh      # Update KQM TCL
python pipeline/2_fetch_structured.py         # Fetch game data (characters, weapons, artifacts)
python pipeline/2_fetch_structured.py --type characters  # Specific data type only
python generate_corpus.py --resume            # Gemini synthesis (skips done files)
python generate_corpus.py --list              # Show all topics to generate
python pipeline/4_fetch_community.py --type all
python pipeline/4_fetch_community.py --character "Kokomi"
```

### Ingest (Pinecone)

```bash
# Ingest all docs
python ingest.py

# Single tier only
python ingest.py --dir docs/generated

# Custom chunking
python ingest.py --chunk-size 300 --chunk-overlap 40

# Full re-index (wipes index first)
python ingest.py --clear
```

## Architecture

### Pipeline Steps (defined in `run_pipeline.py`)

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

3. **synthesize** → `generate_corpus.py --resume`
   - Uses Gemini 2.5 Flash-Lite (15 RPM, 1000 RPD free tier)
   - Generates 600-1200 word entries grounded in Tier 1 data
   - Topics registered in `TOPICS` array (line 81+) as `(category, slug, display_name, prompt_instructions)`
   - Self-throttles with 5-second delays + 65-second retry on rate limits
   - Progress tracked in `logs/progress.json`
   - Outputs to `docs/generated/`

4. **community** → `pipeline/4_fetch_community.py --type all`
   - Fetches Reddit top posts (meta shifts, sentiment)
   - Tagged as "community opinion — not ground truth"
   - Best-effort step (failures don't block pipeline)

5. **wiki** → `pipeline/5_fetch_wiki.py --type all`
   - Scrapes HoYoverse + ambr.top wiki data
   - Best-effort step

6. **ingest** → `ingest.py`
   - Embeds all .md/.txt files from `docs/` using `sentence-transformers/all-MiniLM-L6-v2` (384-dim, local, free)
   - Chunks with 300 word overlap of 40 words by default
   - Upserts to Pinecone in batches of 100
   - Requires `PINECONE_API_KEY` in environment

### GitHub Actions Workflow (`.github/workflows/update_corpus.yml`)

Runs every Sunday at 2am UTC (`cron: "0 2 * * 0"`):

1. Run pipeline steps: tcl, structured, synthesize, community, wiki
2. Commit updated `docs/` back to repo (full audit trail)
3. Ingest into Pinecone (after commit, so docs are saved even if ingest fails)
4. Upload logs as artifacts (14-day retention)

Requires GitHub Actions secrets:
- `GEMINI_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_INDEX` (default: llmops-rag)

### Data Flow

```
KQM/TCL submodule → docs/tcl/           (peer-reviewed theorycrafting)
genshin-db API    → docs/structured/    (exact game stats)
                    ↓
            Gemini synthesis → docs/generated/  (grounded prose)
                    ↓
Reddit API        → docs/community/     (meta signals)
                    ↓
        sentence-transformers → embeddings
                    ↓
                 Pinecone      (vector DB for RAG)
```

### Key Files

- `run_pipeline.py`: Master orchestrator, defines step sequence and runs each script
- `generate_corpus.py`: Large file (16k tokens) with full topic registry starting at line 81
- `pipeline/1_setup_tcl.py`: Git submodule manager, copies files with attribution headers
- `pipeline/2_fetch_structured.py`: genshin-db API client with Windows CP1252 encoding fixes
- `ingest.py`: Standalone Pinecone uploader, no dependency on Irminsul serving repo

### Environment Variables

Required in `.env`:
- `GEMINI_API_KEY` — from https://aistudio.google.com (free tier)
- `PINECONE_API_KEY` — for vector DB ingest
- `PINECONE_INDEX` — index name (default: llmops-rag)

## Important Behaviors

### Rate Limiting (Gemini)

`generate_corpus.py` uses Gemini 2.5 Flash-Lite with strict rate limits:
- 15 requests per minute (RPM)
- 1000 requests per day (RPD)
- Script enforces 5-second delay AFTER each response
- On rate limit (429), waits 65 seconds (full window)
- Each generation takes ~10s response time + 5s delay = ~15s per topic
- Full corpus generation (~80 topics) takes ~20 minutes

### Windows Compatibility

`pipeline/2_fetch_structured.py` includes Windows CP1252 encoding fixes:
- Forces stdout to UTF-8 with `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`
- Uses `safe_log()` wrapper to strip unicode box chars that break Windows terminals
- Logs to both file (UTF-8) and stdout

### Resume Safety

Both `pipeline/2_fetch_structured.py` and `generate_corpus.py` skip already-generated files. Safe to Ctrl+C and resume without re-fetching. Use `--resume` flag for `generate_corpus.py`.

### File Exclusions

- `vendor/TCL/` is excluded from git (`.gitignore`) to avoid submodule conflicts
- Evidence vaults from KQM/TCL are excluded (verbose test logs, not clean knowledge)
- `INDEX.md` files are excluded from Pinecone ingest

## Expected Output

After full pipeline run:
- ~300 files in `docs/tcl/`
- ~500 files in `docs/structured/`
- ~80 files in `docs/generated/`
- ~80 files in `docs/community/`
- Total: ~960 .md files
- Logs in `logs/pipeline.log`, `logs/generation.log`, `logs/fetch_structured.log`, `logs/ingest.log`
- Progress state in `logs/progress.json`, `logs/last_run.json`

## Adding New Topics for Gemini Synthesis

Edit `generate_corpus.py`, add entries to the `TOPICS` array (line 81+):

```python
("category", "slug", "Display Name", "Detailed prompt instructions...")
```

Categories: `reactions`, `mechanics`, `characters`, `weapons`, `team_building`, `spiral_abyss`, `lore`

Each prompt should:
- Be tightly scoped (one topic per file for clean RAG chunking)
- Request specific details (numbers, names, mechanics)
- Specify minimum 600 words (aim for 800-1200)
- Follow the `SYSTEM_PROMPT` rules (line 58-79)

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

## Planned Rebuild (DO NOT use generate_corpus.py as the model for new code)

The current `generate_corpus.py` approach is being REPLACED. Problems:
- Gemini hallucinates details even when prompted carefully
- 15 RPM / 1000 RPD rate limits cause GitHub Actions failures
- LLM-generated prose is not ground truth — it's a liability in a RAG system

New architecture replaces Gemini generation with deterministic scraping:

### New Step 3: `pipeline/3_scrape_wiki.py`
- Source: Genshin Impact Fandom Wiki via MediaWiki API
  - Endpoint: https://genshin-impact.fandom.com/api.php
  - No authentication required, no rate limit issues
  - Returns canonical wikitext per character/topic page
- One .md file per character, one file per major topic
- Strip wikitext markup → clean markdown
- Tag each file with frontmatter: source, page title, scraped date
- Output: docs/wiki/ (new tier, replaces docs/generated/)

### What stays the same:
- pipeline/1_setup_tcl.py — keep as-is
- pipeline/2_fetch_structured.py — keep as-is  
- pipeline/4_fetch_community.py — keep as-is
- ingest.py — keep as-is

### What gets retired:
- generate_corpus.py — DO NOT edit or extend this file
- docs/generated/ — will be replaced by docs/wiki/

### Resume claim this enables:
"Replaced LLM-generated corpus with deterministic MediaWiki API scraping pipeline — 
zero hallucination risk, no rate limits, canonical lore per character auto-updating weekly."
