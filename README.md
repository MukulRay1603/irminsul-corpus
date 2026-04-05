# irminsul-corpus

> Autonomous knowledge base pipeline for [Irminsul](https://github.com/MukulRay1603/Irminsul) — 
> a production RAG assistant for Genshin Impact.

Deterministic corpus builder that pulls peer-reviewed theorycrafting (KQM TCL), exact game stats (genshin-db API), and canonical lore (Fandom Wiki). Runs weekly via GitHub Actions. Each vector carries 7 metadata fields for smart filtering by tier, character, content type, and trust score.

---

## Corpus

| Tier | Source | Files | Trust |
|------|--------|-------|-------|
| TCL  | KQM Theorycrafting Library | 305 | Ground truth |
| Structured | genshin-db API | 405 | Ground truth |
| Wiki | Genshin Impact Fandom Wiki | 130 | Canonical |

Total: 840 files · 6,876 Pinecone vectors · 7 metadata fields per chunk

---

## Pipeline

```
discover → tcl → structured → wiki → ingest
```

Runs every Sunday 2am UTC via GitHub Actions. Auto-discovers new characters when patches drop. Incremental updates only.

---

## Architecture

- Smart name resolver with persistent cache — handles full wiki names automatically
- Incremental timestamp-based updates — only re-fetches pages changed since last run  
- Self-healing structured data — validate_file() detects broken API fields and auto-re-fetches

---

## Setup

```bash
git clone https://github.com/MukulRay1603/irminsul-corpus
cd irminsul-corpus
pip install -r requirements.txt
cp .env.example .env
```

**Required secrets (GitHub Actions):**
- `PINECONE_API_KEY`
- `PINECONE_INDEX`

**Optional (local only):**
- `GEMINI_API_KEY` (legacy, not used in pipeline)

**Run:**
```bash
python run_pipeline.py
```

---

## Attribution & Legal

- **KQM Theorycrafting Library** — © KQM contributors, CC BY-NC-SA 4.0  
  https://github.com/KQM-git/TCL
  
- **genshin-db** — open source game data by theBowja  
  https://github.com/theBowja/genshin-db
  
- **Genshin Impact Fandom Wiki** — community wiki data  
  https://genshin-impact.fandom.com
  
- **Genshin Impact** is the intellectual property of HoYoverse (miHoYo Co., Ltd.)  
  This project is not affiliated with or endorsed by HoYoverse.  
  All game content, characters, and lore belong to HoYoverse.
