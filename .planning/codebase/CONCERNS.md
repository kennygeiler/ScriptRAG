# Codebase Concerns

**Analysis Date:** 2026-04-03

## Tech Debt

**Monolithic UI and analytics modules:**
- Issue: `app.py` and `metrics.py` are very large single modules (dashboard, pipeline orchestration, caching, and many Neo4j-backed analytics live together).
- Files: `app.py`, `metrics.py`
- Impact: Harder refactors, higher merge conflict risk, weaker separation between presentation and query logic.
- Fix approach: Extract tab-level helpers (already partially split via `cleanup_review.py`, `pipeline_runs.py`) and thin `metrics.py` into domain-focused modules without changing public metric definitions (keep aligned with `strategy.md`).

**Script-specific dashboard configuration:**
- Issue: Protagonist regression and power-shift cohort logic assume a fixed lead id (`PROTAGONIST_ID = "zev"`).
- Files: `app.py`
- Impact: Wrong or missing warnings on non–Cinema Four scripts; misleading “regression” signal.
- Fix approach: Config-driven protagonist id (env or project YAML) as already called out in `strategy.md` §3 and §6.

**Global compiled-graph cache in extraction adapter:**
- Issue: `extraction_graph.py` caches compiled LangGraph instances keyed on `lexicon_ids`; changing bundle construction rules without process restart could theoretically desync cache semantics (low probability in typical single-process Streamlit use).
- Files: `extraction_graph.py`, `etl_core/graph_engine.py`
- Impact: Stale graph shape if code hot-reloads but globals persist oddly.
- Fix approach: Version the cache key (e.g. bundle hash) or avoid module-level singletons in long-lived workers.

**Silent failure patterns:**
- Issue: Broad `except Exception: pass` or `return False` hides Neo4j schema/telemetry failures.
- Files: `pipeline_runs.py` (`ensure_pipeline_run_schema`), `app.py` (`_persist_pipeline_run`), `neo4j_loader.py` (telemetry `record_neo4j_loader_ok` wrapped in `OSError` only — other failures still propagate from inner calls, but outer `pass` on OSError swallows disk issues quietly)
- Impact: Missing `:PipelineRun` constraint or failed efficiency persistence with no user-visible error.
- Fix approach: Log at warning level with structured context; optional `st.warning` when persistence fails from UI path.

**Description placeholder in packaging metadata:**
- Issue: `pyproject.toml` still has generic `description = "Add your description here"`.
- Files: `pyproject.toml`
- Impact: Minor; poor PyPI/metadata hygiene if published.
- Fix approach: Replace with accurate ScriptRAG description.

## Known Bugs

**Not separately tracked in code comments:**
- Symptoms: Application Python sources contain no `TODO`/`FIXME` markers; gaps are documented in `strategy.md` (e.g. script-agnostic UI, empty Neo4j handling).
- Files: `strategy.md` §3, §6; dashboard guards in `app.py` for empty query results
- Trigger: Empty or partial graph relative to expected scenes.
- Workaround: Run pipeline through completion and load Neo4j; use sidebar cache reload.

## Security Considerations

**LLM-generated Cypher execution (Investigate tab):**
- Risk: `GraphCypherQAChain` is configured with `allow_dangerous_requests=True` in `agent.py`, so model-produced Cypher runs against the live Neo4j database. Malicious or mistaken queries could read broadly, mutate data if permissions allow writes, or overload the DB.
- Files: `agent.py`
- Current mitigation: Prompt constrains labels and relationship types; intended for trusted local/single-user use.
- Recommendations: For any shared or internet-exposed deployment: disable arbitrary Cypher execution, add a read-only Neo4j user for QA, use LangChain/Neo4j allowlists, or replace with pre-approved query templates plus parameter binding.

**Streamlit deployment surface:**
- Risk: No application-level authentication; destructive actions (e.g. full graph wipe) are available from the UI when reachable on a network.
- Files: `app.py` (`_nuke_neo4j_all_nodes`, sidebar controls)
- Current mitigation: Assumes local or trusted network; optional `DISABLE_PIPELINE` for read-oriented deployments (`strategy.md`, `.env.example`).
- Recommendations: Streamlit Cloud auth, reverse proxy with SSO, or strip dangerous controls in production builds.

**Secrets and environment:**
- Risk: API keys and Neo4j credentials required at runtime; misconfiguration exits CLI tools via `sys.exit`.
- Files: `.env` (not committed), `.env.example`, `metrics.py`, `neo4j_loader.py`, `reconcile.py`, `agent.py`
- Current mitigation: `.env.example` documents variable names only; workspace rules forbid committing secrets.
- Recommendations: Keep parameterized Cypher for all user-derived inputs in custom code paths; never build Cypher from raw Streamlit widgets except via the LLM chain (which remains the highest-risk path above).

**Dynamic Cypher fragments:**
- Risk: `reconcile.py` embeds `label` and relationship ``type`` in query strings. Labels are restricted to `_MERGE_LABELS`; relationship types are validated with `_REL_TYPE_OK` before use in manual merge.
- Files: `reconcile.py`
- Current mitigation: Whitelist labels; regex gate on `type(r)`.
- Recommendations: Keep ids and dynamic segments parameterized (already uses `$keep`, `$drop`, `$props`); add tests for rejection of bad rel types.

## Performance Bottlenecks

**Per-scene LLM extraction:**
- Problem: Full script ingest issues many sequential LLM calls (extract → validate → fix → optional audit).
- Files: `ingest.py`, `extraction_graph.py`, `etl_core/graph_engine.py`, `domains/screenplay/adapter.py`
- Cause: Correctness-first pipeline; no batch API across scenes in-repo.
- Improvement path: Parallelism with rate limits, cheaper model for fix-only passes, or selective audit (already toggleable via `enable_audit`).

**Dashboard Neo4j fan-out:**
- Problem: Several metrics functions open sessions and run multiple queries; cached wrappers reduce repeat cost but cold loads still hit Neo4j heavily.
- Files: `app.py` (`@st.cache_data` wrappers), `metrics.py`
- Cause: Fine-grained queries for clarity.
- Improvement path: Consolidate read queries where graphs share parameters; tune TTL; keep cache stamp tied to artifact mtimes as today.

**Large in-memory artifacts:**
- Problem: `validated_graph.json` and session state can grow with scene count.
- Files: `app.py`, `ingest.py`, `parser.py` outputs under project root
- Cause: Full-graph JSON workflow.
- Improvement path: Chunked storage or DB-first pipeline for very long scripts.

## Fragile Areas

**Assertion-based invariants in loader and engine:**
- Files: `neo4j_loader.py` (`assert rel_type in NARRATIVE_REL_TYPES`, `assert c is not None` in stats), `etl_core/graph_engine.py` (`assert bundle.audit_llm is not None` inside `_build_auditor`)
- Why fragile: Assertions can be stripped with `python -O` or signal programmer errors as crashes in production if miswired.
- Safe modification: Prefer explicit `if` + `raise ValueError`; ensure audit graph is only built when `audit_llm` is present (domain bundle already gates this in normal use).

**Fuzzy matching dependency:**
- Files: `reconcile.py` (`fuzzywuzzy.fuzz`), `pyproject.toml`
- Why fragile: `fuzzywuzzy` is unmaintained; quality depends on `python-Levenshtein` if installed (not declared in `pyproject.toml`), else slower pure-Python path.
- Safe modification: Pin behavior with tests before swapping to `rapidfuzz`; declare optional speed extra in metadata.

**LangGraph / instructor / Anthropic stack:**
- Files: `etl_core/graph_engine.py`, `extraction_llm.py`, `ingest.py`
- Why fragile: Version bumps across LangChain, instructor, or Anthropic SDKs can change token accounting or response shapes.
- Safe modification: Lock versions in `uv.lock`; add smoke tests for one-scene extract.

## Scaling Limits

**Single-process Streamlit + synchronous pipeline:**
- Current capacity: One interactive user running extraction blocks that Python process; no multi-tenant queue.
- Limit: Timeouts or browser disconnects on long scripts.
- Scaling path: Background job worker (RQ/Celery) writing to shared Neo4j; Streamlit as viewer only.

**Neo4j sizing:**
- Current capacity: Tuned for indie feature–length graphs (on the order of 10² scenes, 10³–10⁴ edges).
- Limit: Very dense conflict graphs slow some `metrics.py` aggregations.
- Scaling path: Indexes/constraints on `:Event(number)`, `:Character(id)`; profile slow Cypher with `EXPLAIN`.

## Dependencies at Risk

**fuzzywuzzy:**
- Risk: Unmaintained package; possible future incompatibility with Python or packaging tools.
- Impact: `reconcile.py` duplicate detection and merge UX degrade or break on upgrade.
- Migration plan: Replace with `rapidfuzz` API-compatible calls; revalidate merge thresholds.

**langchain-neo4j + GraphCypherQAChain:**
- Risk: Major-version changes to LangChain often rename APIs; `allow_dangerous_requests` behavior may change.
- Impact: Investigate tab breaks on upgrade.
- Migration plan: Pin upper bounds until a dedicated upgrade task; read upstream migration notes.

## Missing Critical Features

**Automated test suite:**
- Problem: No `tests/` tree or `pytest` dependency in `pyproject.toml`; regressions rely on manual dashboard and CLI checks.
- Blocks: Safe refactors of `metrics.py` formulas and `reconcile.py` merge logic.
- Priority: High for reconciliation and metric-definition changes.

**CI pipeline:**
- Problem: No `.github/workflows` (or other CI) detected in repo.
- Blocks: Enforced lint/test on PRs.
- Priority: Medium once tests exist.

## Test Coverage Gaps

**Metric math and Neo4j loaders:**
- What's not tested: Passivity, narrative momentum, scene heat, act bounds, loader merge behavior, and `reconcile.py` merge rewiring.
- Files: `metrics.py`, `neo4j_loader.py`, `reconcile.py`
- Risk: Silent drift from definitions in `strategy.md` §4.
- Priority: High for `metrics.py` (contract tests against small fixture graph in Neo4j or Docker).

**ETL self-healing loop:**
- What's not tested: `etl_core/graph_engine.py` retry routing, `MaxRetriesError`, audit error handling.
- Files: `etl_core/graph_engine.py`, `extraction_graph.py`
- Risk: LangGraph wiring regressions.
- Priority: Medium (mock LLM stubs).

**Agent / Cypher path:**
- What's not tested: `ask_narrative_mri` and prompt stability.
- Files: `agent.py`
- Risk: Non-deterministic LLM output; harder to unit test without VCR or mock LLM.
- Priority: Low for unit tests; integration smoke with read-only DB user if exposed.

---

*Concerns audit: 2026-04-03*
