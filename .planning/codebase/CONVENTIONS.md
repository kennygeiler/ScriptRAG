# Coding Conventions

**Analysis Date:** 2026-04-03

## Naming Patterns

**Files:**
- Use `snake_case.py` at repo root for top-level modules (`app.py`, `metrics.py`, `neo4j_loader.py`, `ingest.py`).
- Domain-specific code lives under `domains/<domain>/` with the same pattern (`adapter.py`, `rules.py`, `auditors.py`, `schemas.py`).
- Package internals: `etl_core/` uses short descriptive module names (`graph_engine.py`, `telemetry.py`, `errors.py`).

**Functions:**
- Public API: `snake_case` (`get_driver`, `load_entries`, `format_scene_user_message`).
- Internal helpers: leading underscore (`_require_env`, `_merge_event`, `_build_validator`, `_ensure_clients`).
- Callable factories inside engines use nested names like `_build_extractor` returning `_extract`.

**Variables:**
- `snake_case` for locals and parameters (`own`, `drv`, `session`, `gjson`).
- Module-level constants: `UPPER_SNAKE` for tunables and exported sets (`MAX_FIX_ATTEMPTS`, `ENTITY_LABELS`, `ROLLING_SCENES`).
- “Private” module constants may use leading underscore (`_ROOT`, `_MAX_TOKENS`, `_SOURCE_QUOTE_MERGE_SEP`).

**Types:**
- Pydantic models and exception classes: `PascalCase` (`SceneGraph`, `Relationship`, `MaxRetriesError`).
- `TypedDict` for structured dicts: `PascalCase` (`ETLState`, `SceneDict`, `RawSceneDict`).
- Type aliases and literals: `PascalCase` or descriptive caps (`SnakeCaseId`, `EntityLabel`, `RelationshipType`).

**Graph / domain IDs:**
- Character, location, and prop IDs in extracted data are enforced as lexicon-aligned `snake_case` where validated (`schema.py` uses `AfterValidator` for snake_case IDs).

## Code Style

**Formatting:**
- Not detected: no `ruff.toml`, `.ruff.toml`, `pyproject.toml` `[tool.ruff]` / `[tool.black]`, `.pre-commit-config.yaml`, or `mypy.ini` in the repository.
- Match surrounding files when editing; keep line length and wrapping consistent with neighbors (typically Black-like double quotes for strings in new code if ambiguous).

**Linting:**
- Not detected: no configured linter in project manifests.

**Python version:**
- `requires-python = ">=3.12"` in `pyproject.toml`; use 3.12+ syntax (`str | None`, `list[dict[str, Any]]`).

## Import Organization

**Order (observed pattern):**
1. `from __future__ import annotations` as the first line when present.
2. Optional early side effects: `load_dotenv()` / `load_env()` + `enable_langsmith()` immediately after third-party env loaders (`metrics.py`, `neo4j_loader.py`, `ingest.py`, `app.py`).
3. Standard library (`argparse`, `json`, `os`, `sys`, `pathlib`, `typing`, …).
4. Third-party (`neo4j`, `pydantic`, `streamlit`, `langgraph`, `instructor`, `anthropic`, …).
5. First-party: local modules (`from schema import …`, `from etl_core.graph_engine import …`, `from domains.screenplay.adapter import …`).

**Note:** `ingest.py` loads `etl_core.config` before some stdlib imports to run `load_env()` / `enable_langsmith()` before other imports; preserve that ordering when touching that file.

**Path aliases:**
- Not used; imports are flat package-relative from project root (no `src/` layout).

**Exports:**
- `metrics.py` defines `__all__` for the public query surface; other modules rely on implicit exports.

## Error Handling

**Patterns:**
- **Missing configuration (CLI / scripts):** `_require_env` in `metrics.py` and `neo4j_loader.py` prints a clear message and calls `sys.exit(1)`. `extraction_llm.py` does the same for `ANTHROPIC_API_KEY`.
- **Pydantic validation:** Catch `ValidationError` in pipelines (`etl_core/graph_engine.py`, `ingest.py`) to drive retry/fix loops and logging to files (e.g. `failed_scenes.log`), not always to re-raise immediately.
- **Invalid invariants in Python code:** `ValueError` for bad labels or inputs (`neo4j_loader.py` `_merge_entity` when label not in `ENTITY_LABELS`).
- **ETL exhaustion:** `MaxRetriesError` in `etl_core/errors.py` subclasses `RuntimeError` and carries `retry_count` / `last_error`.
- **LLM transport:** `APIStatusError` and `InstructorRetryException` are re-raised from `call_llm_with_usage` in `extraction_llm.py`; primary→fallback wrappers catch broad `Exception` (and `APIStatusError`) to retry on the fallback model—when adding code, avoid swallowing errors silently outside that pattern.
- **Streamlit / UI:** Prefer `st.error` / user-visible messages in `app.py` for recoverable failures; use the same Neo4j env pattern as `metrics.get_driver` when opening drivers.

**Cypher:**
- Use parameterized queries only (`$id`, `$number`, etc.); do not interpolate user or file-derived strings into query text except for static labels already validated in code (see `neo4j_loader.py` pattern for `MERGE (n:Label …)` where `Label` comes from a closed set).

## Logging

**Framework:** Not used for structured logging in core modules reviewed.

**Patterns:**
- `print(..., flush=True)` for operator-facing errors and sanity checks (`schema.py` `main()`, env missing messages).
- **Audit / persistence:** JSON lines append to files (`ingest.py` `_append_audit_entries`, `_append_failed_log`); LangGraph state holds `audit_trail` lists in `ETLState` (`etl_core/state.py`).

## Comments

**When to Comment:**
- Module docstrings explain responsibility and boundaries (`etl_core/graph_engine.py`, `extraction_llm.py`, `cleanup_review.py`).
- Section banners (`# ---------------------------------------------------------------------------`) separate phases in `graph_engine.py`.
- `Field(description=...)` on Pydantic models documents LLM-facing contracts (`schema.py`, `domains/screenplay/schemas.py`).

**Docstrings / typing:**
- Public functions that cross Neo4j or analytics layers often have one-line docstrings (`metrics.py`).
- Prefer type hints on public functions and dataclass fields (`SceneResult` in `ingest.py`).

## Function Design

**Size:** Prefer small node builders in `graph_engine.py` (`_build_extractor`, `_build_validator`) over monoliths; keep Streamlit page logic in `app.py` decomposed into helpers where already done.

**Parameters:**
- Use keyword-only markers for optional driver injection: `*, driver: Driver | None = None` in `metrics.py` to avoid accidental positional args.

**Return Values:**
- LLM wrappers return `tuple[BaseModel, dict[str, Any]]` with usage dicts keyed consistently for `etl_core/telemetry.py` (`accumulate_usage`).
- Metrics functions return plain JSON-serializable structures (`list[dict]`, `dict[str, int]`, `float | None`).

## Module Design

**Exports:** Use `__all__` when defining a stable library surface (`metrics.py`).

**Barrel files:** Not used; import from concrete modules.

**Separation:**
- `etl_core/` stays domain-agnostic; screenplay specifics live in `domains/screenplay/` and are wired via `DomainBundle` (`domains/screenplay/adapter.py`).
- Root `schema.py` holds shared graph shapes; `domains/screenplay/schemas.py` extends or mirrors for the domain where needed—check both when changing extraction shape.

---

*Convention analysis: 2026-04-03*
