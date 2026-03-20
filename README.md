# Irminsul Corpus

> Autonomous, self-updating Genshin Impact knowledge base for the [Irminsul RAG assistant](https://github.com/MukulRay1603/Irminsul).

Runs fully automatically every week via GitHub Actions. Zero manual work after setup.

---

## Data Architecture — Three Tiers of Truth

```
TIER 1 — Ground Truth (zero hallucination risk)
├── docs/tcl/           KQM Theorycrafting Library (peer-reviewed, git submodule)
└── docs/structured/    genshin-db API — exact stats, talents, weapons, artifacts

TIER 2 — Expert Synthesis (grounded prose, Gemini-authored)
└── docs/generated/     Gemini writes WITH Tier 1 data as context
                        Cannot hallucinate stats — the numbers are in the prompt

TIER 3 — Community Signal (opinion, explicitly tagged)
└── docs/community/     Reddit top posts — meta shifts, buff/nerf sentiment
                        Every file tagged: "community opinion — not ground truth"
```

---

## Autonomous Pipeline

```
GitHub Actions — every Sunday 2am UTC
        │
        ├── 1. git pull KQM/TCL submodule     (new theorycrafting findings)
        ├── 2. fetch genshin-db API            (stat changes from patches)
        ├── 3. Gemini synthesizes prose        (grounded in Tier 1)
        ├── 4. Reddit community signals        (meta awareness)
        ├── 5. commit docs/ to this repo       (full audit trail)
        └── 6. trigger Pinecone re-ingest      (Irminsul answers improve)
```

---

## Setup (one time only)

**1. Clone and install**
```bash
git clone https://github.com/YOUR_USERNAME/irminsul-corpus
cd irminsul-corpus
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

**2. Configure**
```bash
cp .env.example .env
# Add GEMINI_API_KEY from https://aistudio.google.com (free)
```

**3. Initialize KQM TCL**
```bash
python pipeline/1_setup_tcl.py --init
```

**4. Run the full pipeline once**
```bash
python run_pipeline.py
```

**5. Add GitHub Actions secrets**

Repo → Settings → Secrets → Actions:
- `GEMINI_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_INDEX` (default: llmops-rag)

After this — pipeline runs itself every Sunday. You're done.

---

## Manual Commands

```bash
python run_pipeline.py                              # full pipeline
python run_pipeline.py --steps tcl structured       # specific steps
python pipeline/1_setup_tcl.py --refresh            # update KQM TCL
python pipeline/2_fetch_structured.py               # fetch game data
python generate_corpus.py --resume                  # Gemini synthesis
python pipeline/4_fetch_community.py --character "Kokomi"
python generate_corpus.py --list                    # see all topics
```

---

## Expected Output (~960 files total)

| Tier | Directory | Files |
|---|---|---|
| KQM TCL | `docs/tcl/` | ~300 |
| Structured | `docs/structured/` | ~500 |
| Synthesized | `docs/generated/` | ~80 |
| Community | `docs/community/` | ~80 |

---

## Using with Irminsul

```bash
python ingest.py --dir /path/to/irminsul-corpus/docs --chunk-size 300 --chunk-overlap 40
```

Or set `IRMINSUL_PATH=/path/to/irminsul` in `.env` to auto-ingest as part of the pipeline.

---

Genshin Impact is owned by HoYoverse. This project is not affiliated with HoYoverse.
