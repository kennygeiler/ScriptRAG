# Codebase Structure

**Analysis Date:** 2026-04-03

## Directory Layout

There is no `src/` package: Python modules live at the repository root alongside config and data artifacts.

```
GraphRAG/
├── etl_core/                 # LangGraph ETL engine (domain-agnostic)
├── domains/
│   └── screenplay/           # DomainBundle: rules, auditors, adapter
├── .planning/
│   └── codebase/             # GSD codebase map (this folder)
├── .cursor/                  # Cursor + bundled GSD (get-shit-done)
├── .claude/                  # Claude Code hooks / GSD mirror
├── app.py                    # Streamlit entry
├── schema.py                 # Pydantic graph contract
├── ingest.py                 # FDX → scenes → extraction orchestration
├── neo4j_loader.py         # JSON → Neo4j (parameterized Cypher)
├── metrics.py                # Analytics queries + helpers
├── extraction_graph.py       # Facade: compile/run LangGraph pipeline
├── extraction_llm.py         # Anthropic + instructor call sites
├── agent.py                  # LangChain graph QA (Investigate tab)
├── cleanup_review.py         # Cleanup Review UI + apply flow
├── pipeline_runs.py          # Pipeline run history (Neo4j)
├── pipeline_state.py         # Local progress / resume state
├── parser.py                 # FDX → raw JSON
├── lexicon.py                # Lexicon build/merge
├── metrics.py                # Dashboard + CLI metrics
├── reconcile.py              # Entity reconciliation (scale path)
├── qa_entities.py            # QA entity dumps
├── debug_export.py           # Debug exports
├── producer_notes.py         # Producer-notes tooling
├── pyproject.toml            # uv / project metadata
├── requirements.txt          # Lock-style pins (see pyproject)
├── docker-compose.yml        # Local stack
├── Dockerfile
├── strategy.md               # Project strategy (authoritative)
├── AGENTS.md                 # Agent / contributor guide
├── MEMORY.md                 # Short snapshot
└── *.json / *.fdx            # Sample data & artifacts (git may vary)
```

## Directory Purposes

**`etl_core/`:**
- Purpose: Generic ETL state machine (extract, validate, fix loops, telemetry).
- Contains: `graph_engine.py`, `state.py`, `telemetry.py`, `errors.py`, `config.py`, `__init__.py`.
- Key files: `etl_core/graph_engine.py` (graph build/run), `etl_core/state.py` (ETLState).
- Subdirectories: None (flat package).

**`domains/screenplay/`:**
- Purpose: Screenplay-specific validation, auditors, and `DomainBundle` wiring.
- Contains: `adapter.py`, `rules.py`, `auditors.py`, `schemas.py`.
- Key files: `domains/screenplay/adapter.py` (`get_bundle()`), `domains/screenplay/rules.py`.
- Subdirectories: Only `screenplay/` under `domains/`.

**Repository root (flat modules):**
- Purpose: CLI scripts, Streamlit app, persistence, metrics, and shared schema.
- Contains: One module per major concern (`app.py`, `ingest.py`, `neo4j_loader.py`, …).
- Key files: `schema.py` (canonical models), `app.py` (UI), `ingest.py` (pipeline driver).
- Subdirectories: N/A at root (siblings are dirs listed above).

**`.planning/`:**
- Purpose: GSD planning artifacts; `codebase/` holds this map for planners/executors.
- Contains: Markdown reference docs.
- Key files: `.planning/codebase/*.md`.

## Key File Locations

**Entry points:**
- `app.py`: Streamlit dashboard (`uv run streamlit run app.py`).
- `ingest.py`, `neo4j_loader.py`, `lexicon.py`, `metrics.py`, `reconcile.py`, `qa_entities.py`, `debug_export.py`, `producer_notes.py`: `if __name__ == "__main__"` CLIs.

**Configuration:**
- `pyproject.toml`: Python project and tool config.
- `requirements.txt`: Dependency pins.
- `.env.example`: Environment variable names (secrets not in repo).
- `docker-compose.yml`, `Dockerfile`, `render.yaml`: deployment/local stack.

**Core logic:**
- `schema.py`: Graph JSON shape, `source_quote` on narrative edges.
- `extraction_graph.py` / `extraction_llm.py`: LLM extraction pipeline.
- `parser.py`: Final Draft XML → scene JSON.
- `neo4j_loader.py`: Load validated graphs into Neo4j.
- `metrics.py`: Cypher-backed analytics for dashboard and CLI.

**Presentation & agents:**
- `app.py`: Tabs (Pipeline, Cleanup Review, Efficiency, Dashboard, Investigate).
- `agent.py`: Natural-language graph Q&A.
- `cleanup_review.py`: Human-in-the-loop cleanup UI.

**Testing:**
- Not detected as a dedicated `tests/` tree in this snapshot; see `TESTING.md` for any pytest or manual verification patterns.

**Documentation:**
- `strategy.md`, `MEMORY.md`, `README.md`, `AGENTS.md`.

## Naming Conventions

**Files:**
- Python modules: `snake_case.py` at repo root or under `etl_core/` / `domains/screenplay/`.
- Data artifacts: `snake_case.json` (e.g., `raw_scenes.json`, `lexicon.json`).
- Screenplay sample: `*.fdx` (Final Draft).

**Directories:**
- `etl_core`, `domains`, `screenplay`: lowercase, domain-oriented nesting under `domains/`.

**Special patterns:**
- `__init__.py` only where needed for packages (`etl_core`, `domains/screenplay`).

## Where to Add New Code

**New dashboard tab or UI block:**
- Primary: `app.py` (follow existing tab patterns).
- Metrics/query helpers: `metrics.py` or small helper module if `app.py` grows further.

**New ETL node or pipeline behavior:**
- Engine: `etl_core/graph_engine.py`, state in `etl_core/state.py`.
- Domain hooks: `domains/screenplay/adapter.py`, `rules.py`, or `auditors.py`.

**New graph types or fields:**
- `schema.py` first; then `neo4j_loader.py` merge logic and any Pydantic validators in domain rules.

**New CLI or batch script:**
- Prefer extending an existing root module with a `main` block to match `ingest.py` / `neo4j_loader.py` patterns; avoid scattering one-off scripts unless requested.

**New external integration:**
- Call sites typically in `extraction_llm.py`, `agent.py`, or `neo4j_loader.py`; document in `INTEGRATIONS.md` when stable.

---

*Structure analysis: 2026-04-03*
