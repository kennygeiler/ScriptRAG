# Architecture

**Analysis Date:** 2026-04-03

## Pattern Overview

**Overall:** Layered monolith with a **domain-injected ETL pipeline** (LangGraph) and a **Streamlit** presentation shell. There is no `src/` package layout: application modules live at the repository root and import each other as a flat Python project.

**Key Characteristics:**
- **Pipeline-first data path:** Final Draft (`.fdx`) → JSON artifacts → LLM extraction → validated scene graphs → Neo4j → read-side analytics and UI.
- **Separation of engine and domain:** `etl_core/` implements a generic extract → validate → fix → (optional audit → audit-fix) graph; screenplay specifics are wired through `DomainBundle` from `domains/screenplay/adapter.py`.
- **Single graph contract:** Pydantic models in `schema.py` define `SceneGraph`, nodes, and `Relationship` (including mandatory `source_quote`). `domains/screenplay/schemas.py` re-exports those models for domain-local imports.
- **Dual LLM stacks:** Anthropic + `instructor` for structured extraction/fix (`extraction_llm.py`); LangChain + `langchain_neo4j` for natural-language graph QA (`agent.py`).

## Layers

**Presentation (Streamlit):**
- Purpose: User-facing tabs for pipeline run, cleanup review, efficiency history, dashboard charts, and “Investigate” chat.
- Location: `app.py`
- Contains: Tab layout, `st.session_state`, Plotly figures, calls into ingest/loader/metrics/agent/cleanup helpers.
- Depends on: `ingest`, `parser`, `lexicon`, `neo4j_loader`, `metrics`, `agent`, `cleanup_review`, `pipeline_runs`, `pipeline_state`.
- Used by: Invoked via `uv run streamlit run app.py` (process entry).

**Orchestration & CLI scripts:**
- Purpose: Long-running or batch workflows (ingest all scenes, load graph, build lexicon, metrics CLI, reconciliation, QA dumps).
- Location: `ingest.py`, `neo4j_loader.py`, `lexicon.py`, `parser.py`, `metrics.py`, `reconcile.py`, `qa_entities.py`, `debug_export.py`, `producer_notes.py`
- Contains: `argparse` `if __name__ == "__main__"` blocks, file I/O to project-root JSON artifacts, progress hooks into `pipeline_state.py`.
- Depends on: Lower layers (ETL, schema, Neo4j driver, optional LLM).
- Used by: Operators and the Streamlit Pipeline tab (in-process calls, not subprocess).

**ETL engine (domain-agnostic):**
- Purpose: LangGraph `StateGraph` over `ETLState`: extract, validate, conditional fix loop, optional LLM audit and audit-fix loop; telemetry aggregation.
- Location: `etl_core/graph_engine.py`, `etl_core/state.py`, `etl_core/telemetry.py`, `etl_core/errors.py`, `etl_core/config.py`
- Contains: `DomainBundle` dataclass, `build_graph`, `run_pipeline`, `MaxRetriesError`.
- Depends on: LangGraph, Pydantic only at boundaries (injected model type).
- Used by: `extraction_graph.py` (facade), never imported by `domains/*` from `etl_core` in reverse for screenplay rules (adapter pulls from both sides).

**Screenplay domain adapter:**
- Purpose: Bind `SceneGraph` validation, business rules, and Anthropic call sites into a `DomainBundle`.
- Location: `domains/screenplay/adapter.py`, `domains/screenplay/rules.py`, `domains/screenplay/auditors.py`, `domains/screenplay/schemas.py`, `domains/screenplay/__init__.py`
- Contains: `get_bundle()`, lexicon-aware `validate_business_logic`, combined LLM auditors.
- Depends on: `schema.py` (canonical models), `extraction_llm.py`.
- Used by: `extraction_graph.py`.

**LLM & extraction facade:**
- Purpose: Stable `run_extraction_pipeline` API for `ingest.py`; compile/cache LangGraph per lexicon id set; Anthropic client wiring and instructor calls.
- Location: `extraction_graph.py`, `extraction_llm.py`
- Depends on: `domains/screenplay/adapter.py`, `etl_core/graph_engine.py`, `schema.py`.
- Used by: `ingest.py`.

**Schema & validation:**
- Purpose: Authoritative JSON shape for one scene’s graph; relationship types and snake_case id rules.
- Location: `schema.py`
- Contains: `SceneGraph`, `Relationship`, discriminated `GraphNode`, etc.
- Depends on: Pydantic only.
- Used by: Ingest, loader, domain rules, extraction.

**Persistence & analytics:**
- Purpose: Write validated JSON into Neo4j (merge events, entities, `IN_SCENE`, narrative rels with quote merging); parameterized Cypher for metrics and pipeline run history.
- Location: `neo4j_loader.py`, `metrics.py`, `pipeline_runs.py`
- Contains: Transactional load, wipe that preserves `:PipelineRun`, dashboard query functions, `get_driver()`.
- Depends on: `neo4j` driver, env vars `NEO4J_*`.
- Used by: `app.py`, CLI loaders, `agent.py` (via LangChain graph).

**Supporting UI logic:**
- Purpose: Cleanup Review copy, warning keys, graph deltas without bloating `app.py`.
- Location: `cleanup_review.py`
- Depends on: stdlib + typing; JSON-shaped dicts from session state.
- Used by: `app.py`.

**Cross-cutting state file:**
- Purpose: Durable ingest progress and last successful Neo4j load metadata for CLI and Streamlit.
- Location: `pipeline_state.py`, artifact `pipeline_state.json` at repo root.
- Depends on: `pathlib`, `json`.
- Used by: `ingest.py`, `neo4j_loader.py`, `app.py` (cache stamps).

## Data Flow

**End-to-end screenplay pipeline:**

1. **Parse:** `parser.parse_fdx_to_raw_scenes` reads `.fdx` XML → list of scene dicts (`number`, `heading`, `content`); optionally `write_raw_scenes_json` → `raw_scenes.json`.
2. **Lexicon:** `lexicon.build_master_lexicon` (and related) consumes `raw_scenes.json` → `master_lexicon.json` / `lexicon.json` with canonical character/location ids for the LLM prompt.
3. **Extract (per scene):** `ingest.extract_scenes()` formats each scene as user message text, builds system prompt via `ingest.build_system_prompt`, calls `extraction_graph.run_extraction_pipeline` → LangGraph in `etl_core/graph_engine.py` with bundle from `domains/screenplay/adapter.py` → validated `SceneGraph` JSON + audit trail + warnings + token/cost telemetry.
4. **Checkpoint:** `ingest` appends/rewrites `validated_graph.json` and updates `pipeline_state.update_ingest_progress`.
5. **Review (optional):** Streamlit Cleanup Review mutates in-memory graph using `cleanup_review` helpers; user approves warnings and loads.
6. **Load:** `neo4j_loader.load_entries` merges `:Event`, `:Character`/`:Location`/`:Prop`, `IN_SCENE`, and narrative relationships; wipe excludes `:PipelineRun` nodes.
7. **Analyze & display:** `metrics.py` functions run Cypher; `app.py` caches results with `@st.cache_data` keyed on artifact mtimes; Plotly charts and tables.
8. **Efficiency log:** `pipeline_runs.save_pipeline_run` creates a `:PipelineRun` node after pipeline completion (from `app.py`).

**Investigate (NL → Cypher):**

1. User question in `app.py` → `agent.ask_narrative_mri` (or related entry).
2. `agent.py` uses `Neo4jGraph` + `GraphCypherQAChain` with a fixed template prompt constraining labels and relationship types to the screenplay model.
3. Results are grounded in query output; no separate write path.

**State Management:**
- **Streamlit:** `st.session_state` holds uploaded file state, extraction results, cleanup decisions, and chart inputs.
- **Disk:** JSON artifacts at repo root (`raw_scenes.json`, `master_lexicon.json`, `validated_graph.json`, `pipeline_state.json`, optional `extraction_audit.jsonl`, `failed_scenes.log`).
- **Neo4j:** System of record for loaded graph + `PipelineRun` telemetry nodes.

## Key Abstractions

**`DomainBundle` (`etl_core/graph_engine.py`):**
- Purpose: Inject pydantic model type, deterministic business rules, and three LLM callables (extract, fix, optional audit) into the generic graph.
- Examples: `etl_core/graph_engine.py` (`DomainBundle`), `domains/screenplay/adapter.py` (`get_bundle`).
- Pattern: Dependency injection / ports-and-adapters for the ETL engine.

**`ETLState` (`etl_core/state.py`):**
- Purpose: TypedDict carried through LangGraph nodes (`raw_text`, `system_prompt`, `current_json`, retries, `audit_trail`, `warnings`, token/cost totals).
- Pattern: Reducer-free state updates returned as partial dicts from each node.

**`SceneGraph` (`schema.py`):**
- Purpose: One scene’s nodes and relationships as validated JSON before load.
- Pattern: Pydantic v2 models with discriminators and constrained relationship literals.

**`SceneResult` (`ingest.py`):**
- Purpose: Per-scene outcome for UI progress and logging (`ok`, `fixed`, `failed`, etc.) with optional `graph_entry`, warnings, telemetry.

**Neo4j merge helpers (`neo4j_loader.py`):**
- Purpose: `_merge_event`, `_merge_entity`, `_merge_in_scene`, relationship deduplication and `source_quote` merging for selected types.
- Pattern: One transaction flow with parameterized Cypher strings (no user-built query strings from UI in loader; metrics use fixed Cypher).

## Entry Points

**Streamlit app:**
- Location: `app.py`
- Triggers: `streamlit run app.py`
- Responsibilities: Full product UI, orchestrating parse/lexicon/extract/load paths, dashboard queries, sidebar destructive actions (scoped Neo4j nuke vs full delete documented in code).

**Ingest CLI:**
- Location: `ingest.py` (`if __name__ == "__main__"`)
- Triggers: `uv run python ingest.py` with documented flags (e.g. `--fresh`).
- Responsibilities: Batch extraction, audit logging, failure logs.

**Loader CLI:**
- Location: `neo4j_loader.py` (`if __name__ == "__main__"`)
- Triggers: `uv run python neo4j_loader.py` (arguments per module).
- Responsibilities: Load `validated_graph.json` into Neo4j.

**Parser / lexicon / metrics / reconcile / QA / debug:**
- Locations: `parser.py`, `lexicon.py`, `metrics.py`, `reconcile.py`, `qa_entities.py`, `debug_export.py` — each exposes `if __name__ == "__main__"` for CLI use.
- Responsibilities: Single-purpose tools aligned with `strategy.md` stage table.

**Agent smoke:**
- Location: `agent.py` (`if __name__ == "__main__"`)
- Triggers: Direct run for testing QA chain.

## Error Handling

**Strategy:** Fail fast on missing Neo4j env in CLI modules (`_require_env` + `sys.exit` in `metrics.py`, `neo4j_loader.py`, `reconcile.py` pattern). In the LangGraph pipeline, validation errors route to fix retries; exhausted retries raise `MaxRetriesError` from `etl_core/errors.py`, caught in `extraction_graph.run_extraction_pipeline` and surfaced as failed scenes in `ingest`. Streamlit paths swallow some Neo4j persistence errors for pipeline run logging (`app.py` `_persist_pipeline_run` try/except) to avoid breaking the UI.

**Patterns:**
- Pydantic `ValidationError` in extract/fix and post-pipeline `SceneGraph.model_validate` in `extraction_graph.py`.
- Anthropic `APIStatusError` handling in `ingest.py` for API failures.
- Optional LLM audit failures downgrade to warnings in `etl_core/graph_engine.py` (`audit` node exception path).

## Cross-Cutting Concerns

**Logging:** No centralized logging framework; progress via Streamlit widgets, append-only `extraction_audit.jsonl`, `failed_scenes.log`, and print to stdout in CLI modules.

**Validation:** Pydantic at extraction boundary; additional deterministic checks in `domains/screenplay/rules.py`; optional LLM auditors in `domains/screenplay/auditors.py`.

**Authentication:** Not applicable for the app (local/tooling). Neo4j credentials via environment variables only.

**Configuration:** `python-dotenv` loaded early in `app.py`, `ingest.py` (via `etl_core.config.load_env`), `metrics.py`, `neo4j_loader.py`, `agent.py`, `lexicon.py`, `reconcile.py`. Optional LangSmith toggles via `etl_core.config.enable_langsmith`. Feature flag `DISABLE_PIPELINE` read in `app.py` for hiding the Pipeline tab.

---

*Architecture analysis: 2026-04-03*
