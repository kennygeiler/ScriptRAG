# Technology Stack

**Analysis Date:** 2026-04-03

## Languages

**Primary:**
- Python 3.12 — application, ETL, dashboard, CLI-style scripts (`requires-python` in `pyproject.toml`; base image `python:3.12-slim-bookworm` in `Dockerfile`)

**Secondary:**
- Not applicable (no TypeScript/JavaScript application source; Streamlit serves the UI from Python)

## Runtime

**Environment:**
- CPython 3.12 (local, Docker)

**Package Manager:**
- uv (Astral) — install and lockfile management per `README.md` / `AGENTS.md`
- Lockfile: present at `uv.lock` (use `uv sync --frozen` in `Dockerfile`)

## Frameworks

**Core:**
- Streamlit 1.55.0 — primary web UI (`app.py`)
- LangGraph 1.1.3 — extract → validate → fix → audit pipeline (`etl_core/graph_engine.py`, `extraction_graph.py`, `ingest.py`)
- Pydantic 2.12.5 — schemas and validation (`schema.py`, ETL state)

**Data / viz:**
- Plotly 6.6.0 — charts in Streamlit (`app.py`; `pyproject.toml` allows `>=5.24.0`, lock resolves to 6.6.0)

**LLM orchestration (secondary paths):**
- LangChain Core 1.2.23 (transitive) — prompts and chains (`agent.py`)
- langchain-anthropic 1.4.0 — `ChatAnthropic` for Investigate tab QA (`agent.py`)
- langchain-neo4j 0.9.0 — `Neo4jGraph`, `GraphCypherQAChain` (`agent.py`)

**Testing:**
- Not detected — no `pytest` / `unittest` config or `*_test.py` / `test_*.py` files in repo root tree

**Build / Dev:**
- Docker — multi-stage image with uv (`Dockerfile`)
- docker-compose — local stack (`docker-compose.yml`, `docker-compose.stack.yml`)

## Key Dependencies

**Critical:**
- anthropic 0.86.0 — Messages API for extraction and lexicon (`extraction_llm.py`, `lexicon.py`)
- instructor 1.14.5 — structured outputs on Anthropic client (`extraction_llm.py`, `lexicon.py`, `domains/screenplay/auditors.py`)
- neo4j 6.1.0 — Bolt driver for graph load and metrics (`neo4j_loader.py`, `metrics.py`, `pipeline_runs.py`, `agent.py`, `reconcile.py`, `qa_entities.py`, `debug_export.py`, `producer_notes.py`)
- fuzzywuzzy 0.18.0 — string similarity in reconciliation (`reconcile.py`)
- python-dotenv 1.2.2 — load `.env` (`etl_core/config.py`, `neo4j_loader.py`, `agent.py`, several scripts)

**Infrastructure / transitive (not direct app code):**
- httpx, jiter, anyio — used by `anthropic` SDK
- langsmith — optional tracing when LangChain/LangGraph emit traces (env-driven via `etl_core/config.py`)

## Configuration

**Environment:**
- Load via `python-dotenv` from project `.env` (see names only in `.env.example`; do not commit secrets)
- Key variables: `ANTHROPIC_API_KEY`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, optional LangSmith (`LANGCHAIN_*`), optional `PERSISTENT_DATA_DIR`, optional `DISABLE_PIPELINE` (documented in `.env.example`; pipeline gating in `app.py`)

**Build:**
- `pyproject.toml` — project metadata and dependency ranges
- `uv.lock` — resolved versions for reproducible installs
- `requirements.txt` — pointer to uv workflow (not a flat pin list)
- `render.yaml` — Render Blueprint (web service env var keys, disk mount)
- `Dockerfile` — `uv sync --frozen --no-install-project --no-dev`

## Platform Requirements

**Development:**
- Python ≥3.12, uv, optional local or remote Neo4j; run app with `uv run streamlit run app.py` (per `README.md` / `AGENTS.md`)

**Production:**
- Docker image exposes 8501; `PORT` respected for PaaS (`Dockerfile` / README)
- Typical target: Render (blueprint in `render.yaml`) with Neo4j URI pointing to Aura or co-located instance

---

*Stack analysis: 2026-04-03*
