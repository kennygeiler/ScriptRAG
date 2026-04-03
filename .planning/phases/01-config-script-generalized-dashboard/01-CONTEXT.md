# Phase 1: Config & script-generalized dashboard - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver **config-driven protagonist/lead identifiers** and **script-agnostic dashboard presentation** so operators can analyze arbitrary screenplays without editing Python constants in `app.py` (CONFIG-01, GEN-01). Does **not** include empty-state hardening (Phase 2), reconciliation UX (Phase 3), or complexity signals (Phase 4).

</domain>

<decisions>
## Implementation Decisions

### Configuration source & precedence

- **D-01:** **Environment variables first** — add documented vars (e.g. protagonist id) alongside existing `NEO4J_*` / `ANTHROPIC_API_KEY` pattern in `.env.example`. Matches deployment (Render, Docker) and current project norms.
- **D-02:** **Optional file config (Claude discretion)** — if a single env var is insufficient for display-name maps or multiple tracked leads, use a **small repo-root file** (e.g. `scriptrag.toml` or `scriptrag.yaml`) with an **example** committed (`scriptrag.example.toml`) and real file gitignored or env-pointed. Prefer TOML/YAML over adding Streamlit-only secrets UI in this phase unless trivial.

### Which identifiers and constants move out of code

- **D-03:** **Minimum for CONFIG-01:** Replace hardcoded `PROTAGONIST_ID = "zev"` in `app.py` with value from **env** (required for regression warning path). Keep backward-compatible default only if unset **only during transition** — prefer explicit unset → clear sidebar message (see D-06).
- **D-04:** **`TOP_INTERACTION_CHARACTERS` (currently 5)** — make overridable via env (integer) in same pass if low cost; otherwise defer note in plan.
- **D-05:** Do **not** expand scope to every magic string in the repo in one plan; **GEN-01** focuses on **dashboard tab** user-visible copy and chart labels that assume fixed Cinema Four roles.

### Reload & caching

- **D-06:** **Document** that changing config requires **Streamlit restart** (or container redeploy). **Optional stretch:** invalidate relevant `@st.cache_data` keys when an optional config file mtime changes — planner may include if trivial; otherwise Phase 1 ships restart semantics only.

### Behavior when protagonist id is missing from graph

- **D-07:** If the configured protagonist id is **absent** from the act passivity matrix / graph, show an **`st.info` or sidebar notice** (“Protagonist id `x` not found in loaded graph”) and **skip** the regression warning — no silent failure, no picking an arbitrary character.

### Display names & GEN-01 copy

- **D-08:** User-facing character labels in charts/warnings should use **Neo4j/lexicon display naming** where the data path already provides it; otherwise show the **canonical snake_case id** — avoid hardcoded proper names in new strings.
- **D-09:** Regression warning copy stays **generic** (“the protagonist”) with the **resolved id/label** interpolated from data — no script-specific flavor text.

### Claude's Discretion

- Exact env var names (`SCRIPTRAG_*` vs `SCRIPT_RAG_*`) — follow shortest consistent prefix and update `.env.example` once.
- Whether to introduce `pydantic-settings` vs manual `os.environ` — match **existing** `app.py` / project patterns (`CONVENTIONS.md`); avoid new dependency unless already justified.

### Folded Todos

(None — `todo match-phase` returned no matches.)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap & requirements

- `.planning/ROADMAP.md` — Phase 1 goal, success criteria, UI hint
- `.planning/REQUIREMENTS.md` — CONFIG-01, GEN-01
- `.planning/PROJECT.md` — vision, constraints, validated stack

### Product authority

- `strategy.md` — metric definitions, dashboard map, protagonist regression behavior, script-agnostic direction
- `MEMORY.md` — compact dashboard/metric notes

### Codebase map

- `.planning/codebase/ARCHITECTURE.md` — Streamlit shell, metrics, `app.py` entry
- `.planning/codebase/STRUCTURE.md` — where new config helpers should live
- `.planning/codebase/CONVENTIONS.md` — Python / project patterns

### Implementation touchpoints

- `app.py` — `PROTAGONIST_ID`, `_protagonist_regression_warning`, `_extra` / act matrix wiring, dashboard captions (~L41–L451+)
- `.env.example` — add new variable names (no secrets)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets

- **`_env_truthy`** and env patterns in `app.py` for feature flags (`DISABLE_PIPELINE`).
- **Cached dashboard loaders** — `_cached_act_passivity_matrix`, `_DASH_STAMP` / `_neo4j_dashboard_cache_stamp`; config changes must interact correctly with cache keys (restart or explicit clear).

### Established patterns

- **Single-module Streamlit app** — wide layout, `st.session_state`, Plotly charts; new config should stay readable at module top or small helper module at repo root if `app.py` grows.
- **Parameterized Cypher** in `metrics.py` — do not break when adding config-driven ids.

### Integration points

- Protagonist id flows: **act passivity matrix** → **`_protagonist_regression_warning`**; **power shift** top-character list composition (`_extra` tuple).
- **Sidebar** — appropriate place for “current protagonist id” debug/readout for operators.

</code_context>

<specifics>
## Specific Ideas

- **strategy.md** explicitly calls out `PROTAGONIST_ID` constant and Cinema Four–centric defaults as technical debt to generalize.
- User did not supply alternate product references in this discuss session; defaults above align with roadmap success criteria.

</specifics>

<deferred>
## Deferred Ideas

- **Phase 2:** Empty / partial Neo4j and DataFrame hardening (REL-01).
- **Phase 3:** Reconciliation operator surfaces (REC-01).
- **Phase 4:** Production complexity signal (MET-01).
- **Auto-pick “main character” from graph** (e.g. max degree) — out of scope; config remains explicit per D-07.

### Reviewed Todos (not folded)

(None.)

</deferred>

---

*Phase: 01-config-script-generalized-dashboard*
*Context gathered: 2026-04-03*
