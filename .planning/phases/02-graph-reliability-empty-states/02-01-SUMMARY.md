---
phase: 02-graph-reliability-empty-states
plan: 01
subsystem: ui
tags: [streamlit, neo4j, streamlit-cache, logging]

requires:
  - phase: 01-config-script-generalized-dashboard
    provides: lead_resolution, script-agnostic dashboard wiring
provides:
  - Safe `@st.cache_data` Neo4j loaders returning empty sentinels on failure + `logging.exception`
  - Momentum / payoff / power-shift DataFrame and id guards
  - Lazy `Neo4jGraph` + `GraphCypherQAChain` in `agent.py` (import without KeyError)
  - Investigate tab try/except with optional technical expander
  - Cleanup Review safe correction + audit_entries iteration
affects: [phase-03-reconciliation]

tech-stack:
  added: []
  patterns:
    - "Neo4j errors in cached loaders: never `st.*`; log and return empty shape"
    - "Investigate: `_get_chain()` with `_chain_init_failed` to avoid repeat init storms"

key-files:
  created: []
  modified: [app.py, agent.py]

key-decisions:
  - "Dual except: Neo4j transport/auth family then broad Exception, both `_log.exception`"
  - "Power shift uses `valid_chars` filter before plotting"

patterns-established:
  - "Chart renderers verify required columns before `df[...]` indexing"

uat_notes:
  - "With Neo4j stopped: cached loaders return empty data → existing `st.info` paths; Efficiency tab still `st.error`"
  - "With `.env` present: `import agent` succeeds; missing vars yield friendly string from `ask_narrative_mri`"
---

# Phase 2 plan 01 — Summary

**Executed:** 2026-04-03  
**Requirement:** REL-01

## What shipped

- **`app.py`:** All seven `_cached_*` functions wrap Neo4j work in inner try/except; `AuthError` / `Neo4jError` / `ServiceUnavailable` / `OSError` plus broad `Exception`; `_log.exception` on failure; documented return sentinels. Event count uses `rec.get("c", 0)`. Momentum requires `heat` column with non-all-NaN; payoff requires `id`, `first_scene`, `last_scene`, `gap`. Power shift filters `valid_chars`. `_ids_tuple` skips malformed rank rows. Cleanup corrections use `.get` and skip non-dict / bad `audit_entries`. Investigate wraps `ask_narrative_mri` with friendly message + optional `Technical detail` expander (exception type only).

- **`agent.py`:** Lazy `_get_chain()`; missing env or init failure sets `_chain_init_failed`; `ask_narrative_mri` returns fixed strings when chain unavailable or `invoke` fails.

## Verification

- `ast.parse` on `app.py` / `agent.py`: OK  
- `import agent`: OK  
- Linters: no issues on touched files

## Follow-ups (optional)

- Automated tests for cached sentinels (would require mocking driver).
