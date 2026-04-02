```
  ___         _      _   ___    _    ___
 / __| __ _ _(_)_ __| |_| _ \  /_\  / __|
 \__ \/ _| '_| | '_ \  _|   / / _ \| (_ |
 |___/\__|_| |_| .__/\__|_|_\/_/ \_\\___|
               |_|
           screenplay structure you can measure.
```

> upload a screenplay → self-healing AI extraction → human review → neo4j graph → explore with charts and chat. pacing, agency, and long-horizon props—with **verbatim quotes** on every narrative edge. built for writers who want **physics**, not vibes.

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-graph-008cc1.svg)](https://neo4j.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B.svg)](https://streamlit.io/)
[![uv](https://img.shields.io/badge/uv-astral-915C83.svg)](https://github.com/astral-sh/uv)
[![Claude](https://img.shields.io/badge/extract-Claude%20%2B%20Instructor-D4A574.svg)](https://github.com/jxnl/instructor)

## the problem

coverage is subjective. "does act two drag?" "is my protagonist reactive?" "did we forget the gun?" you get opinions. you don't get **reproducible** answers tied to the actual script.

**scriptrag** turns a screenplay into a **queryable graph**: who conflicts with whom, in which scene, with **proof text** on the relationship. from that graph you compute **momentum** (rolling friction), **passivity by act**, and **long-arc props**.

full detail lives in [`strategy.md`](strategy.md). quick context: [`MEMORY.md`](MEMORY.md). agents: [`AGENTS.md`](AGENTS.md).

## table of contents

- [how it works](#how-it-works)
- [the pipeline](#the-pipeline)
- [dashboard](#dashboard)
- [quick start](#quick-start)
- [environment variables](#environment-variables)
- [deployment](#deployment)
- [project structure](#project-structure)
- [license](#license)

## how it works

### the flow (real modules, not a toy diagram)

| step | module | what happens |
|------|--------|----------------|
| **parse** | `parser.py` | `.fdx` xml → `raw_scenes.json`. **no llm.** |
| **lexicon** | `lexicon.py` | whole script text → claude + pydantic → `master_lexicon.json` (stable `snake_case` ids). |
| **ingest** | `ingest.py` + `schema.py` | **per scene**: claude + **instructor** → `SceneGraph`; self-healing loop (extract → validate → fix up to 3 retries); edges need `source_id`, `target_id`, `type`, **`source_quote`**. |
| **load** | `neo4j_loader.py` | merge `:Character` `:Location` `:Prop` `:Event`, `IN_SCENE`, narrative rels. |
| **analyze** | `metrics.py` | parameterized cypher → momentum, payoff props, passivity windows, etc. |
| **ui** | `app.py` | streamlit + plotly. four tabs: pipeline, editor agent, dashboard, investigate. |

neo4j does **not** read english. it stores **nodes and edges**. streamlit asks **metrics**; metrics ask **cypher**.

### the pipeline

```
  FDX              PARSER              RAW JSON
   │                  │                    │
   │  screenplay.xml │                    │
   └─────────────────▶│  ElementTree       │
                      │  scenes + text     │
                      └─────────┬──────────┘
                                │
                                ▼
                      ┌─────────────────┐
                      │  LEXICON        │◀── claude + pydantic
                      │  (all scenes)   │     master cast/locs
                      └────────┬────────┘
                               │
                               ▼
                      ┌─────────────────┐
                      │  INGEST         │◀── claude + instructor
                      │  (per scene)    │     extract → validate → fix
                      │  Editor Agent   │     self-healing loop
                      └────────┬────────┘
                               │
                               ▼
               validated_graph.json (checkpointed)
                               │
                               ▼
                      ┌─────────────────┐
                      │  NEO4J LOADER   │
                      │  MERGE graph    │
                      └────────┬────────┘
                               │
                               ▼
                      ┌─────────────────┐
                      │  NEO4J          │
                      │  bolt / aura    │
                      └────────┬────────┘
                               │
                               ▼
                      ┌─────────────────┐
                      │  STREAMLIT      │
                      │  metrics.py     │
                      └─────────────────┘
```

**important corrections** vs a lazy "ai tags the script" story:

- **`parser.py` never calls an api.** only **`lexicon.py`** and **`ingest.py`** (and **`agent.py`** for chat) use the model.
- pydantic + instructor **enforce** edge shape; bad structured output **retries or fails**—it doesn't silently save junk.
- the **editor agent** (self-healing loop in `etl_core`) validates every extraction against pydantic schemas and deterministic business rules. when validation fails, an llm fixer rewrites the output—and you see every correction in the ui.

## dashboard

wide-layout streamlit. four tabs:

| tab | what it is |
|-----|------------|
| **pipeline** | upload `.fdx`, run full extraction in-process with live per-scene progress. the editor agent monitors every scene: shows pass/fix/fail status, running token + cost totals. |
| **editor agent** | review corrections made by the ai fixer. before/after json diffs for every scene where the editor intervened. "approve & load to neo4j" when satisfied. |
| **dashboard** | **narrative momentum** (per-scene heat = `CONFLICTS_WITH / (INTERACTS_WITH + CONFLICTS_WITH)`, 3-scene rolling mean, dashed act boundaries), **payoff matrix** (long-horizon props > 10 scene gap), **power shift** (passivity index for top 5 characters by act). x/n scenes banner. `st.warning` if protagonist regresses. |
| **investigate** | ask questions about the script's structure via natural language → cypher (`agent.py`). |

pipeline tab is hidden when `DISABLE_PIPELINE=1` (read-only deployments).

## quick start

### five minutes: cold run

```bash
git clone https://github.com/kennygeiler/GraphRAG.git
cd GraphRAG
uv sync
cp .env.example .env
# fill ANTHROPIC_API_KEY + NEO4J_* (local desktop, docker, or aura)

uv run streamlit run app.py
```

open **http://localhost:8501**. upload your `.fdx` in the **pipeline** tab and click **run pipeline**. review corrections in the **editor agent** tab, then approve to load into neo4j.

### cli alternative (headless)

```bash
uv run python parser.py path/to/script.fdx
uv run python lexicon.py raw_scenes.json
uv run python ingest.py
uv run python neo4j_loader.py
uv run streamlit run app.py
```

ingest **checkpoints**; re-run or `ingest.py --resume` if it stops mid-script.

## environment variables

copy [`.env.example`](.env.example) → `.env`. **never commit `.env`.**

```env
ANTHROPIC_API_KEY=sk-ant-...
NEO4J_URI=neo4j://localhost:7687    # or neo4j+s://… for aura
NEO4J_USER=neo4j
NEO4J_PASSWORD=...

# read-only deployment: hide pipeline tab
# DISABLE_PIPELINE=1

# optional: langsmith
# LANGCHAIN_API_KEY=...
# LANGCHAIN_TRACING_V2=false
```

## deployment

there is **no** single button that provisions **both** neo4j aura and the app. aura is always a short separate signup. after that, the repo is set up for **docker** + **render blueprint**.

### fastest cloud shape

| step | action |
|------|--------|
| 1 | create [neo4j aura](https://neo4j.com/cloud/) → copy bolt uri + password. |
| 2 | push repo → [render](https://dashboard.render.com) **new → blueprint** → select repo → [`render.yaml`](render.yaml) → set secret `NEO4J_*` + `ANTHROPIC_API_KEY`. |
| 3 | open the app, upload your `.fdx`, run the pipeline, approve, explore. |

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### docker (local or any host)

```bash
docker build -t scriptrag .
docker run --rm -p 8501:8501 --env-file .env scriptrag
```

`Dockerfile` respects **`PORT`** for render/fly/railway.

### one machine: neo4j + app

```bash
printf '%s\n' 'NEO4J_PASSWORD=your-secure-password' > .env
docker compose -f docker-compose.stack.yml up --build -d
```

open **http://localhost:8501**, upload your screenplay, and run the pipeline from the browser.

### reviewer handoff

- **url only:** deploy dashboard against a pre-loaded aura; share https link.
- **private git:** invite + `.env.example` → `.env` + `uv sync` + `streamlit run app.py`.
- screenplay / json may be sensitive—keep repos private and align with your nda.

## project structure

```
GraphRAG/
├── etl_core/                  # domain-agnostic self-healing ETL engine
│   ├── config.py              #   .env + langsmith bootstrap
│   ├── state.py               #   langgraph ETLState (tokens, cost, audit)
│   ├── telemetry.py           #   anthropic pricing + accumulate_usage
│   ├── errors.py              #   MaxRetriesError
│   └── graph_engine.py        #   langgraph: extract → validate → fix loop
├── domains/
│   └── screenplay/            # screenplay-specific domain plug-in
│       ├── schemas.py         #   re-exports SceneGraph, Relationship
│       ├── rules.py           #   deterministic validation (no AI)
│       └── adapter.py         #   DomainBundle wiring LLM + rules
├── parser.py                  # .fdx → raw_scenes.json (xml only)
├── lexicon.py                 # claude → master_lexicon.json
├── ingest.py                  # per-scene extraction (exports extract_scenes generator)
├── extraction_llm.py          # anthropic + instructor calls (with usage)
├── extraction_graph.py        # thin adapter → etl_core pipeline
├── neo4j_loader.py            # json → neo4j (exports load_entries)
├── schema.py                  # pydantic graph contract
├── metrics.py                 # cypher analytics
├── app.py                     # streamlit: pipeline + editor agent + dashboard + investigate
├── agent.py                   # nl → cypher
├── Dockerfile
├── docker-compose.yml         # app → external neo4j / aura
├── docker-compose.stack.yml   # neo4j + app on one host
├── render.yaml                # render blueprint
├── strategy.md                # authoritative project brain
├── MEMORY.md
└── AGENTS.md
```

## license

add a license (e.g. mit) when you publish the repo.
