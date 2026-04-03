# Requirements — ScriptRAG (GSD)

**Active tracks:** **v1.2** (demo / data-out flow) and **v1.1** (quality & open-source hygiene) — see `.planning/ROADMAP.md` for phase order.

## v1.2 Requirements — Demo & data-out flow

### Product flow

- [x] **OUT-01**: **Data out** tab — schema card, live Neo4j label/rel counts, fixed **recipe Cypher** (parameterized), CSV export for narrative edges (capped), characters, events. *Phase 8 — shipped 2026-04-03 (`08-01-SUMMARY.md`).*
- [x] **FLOW-01**: **HITL + observability narrative** — Cleanup HITL gate banner; Efficiency tab frames **:PipelineRun** as agentic pipeline telemetry. *Phase 9 — shipped 2026-04-03 (`09-01-SUMMARY.md`).*
- [x] **DEMO-01**: **`SCRIPTRAG_DEMO_LAYOUT`** reorders tabs (Cleanup → Data out → Reconcile…); demo sidebar + Investigate copy. *Phase 10 — shipped 2026-04-03 (`10-01-SUMMARY.md`).*

## v1.1 Requirements

### Quality & tests

- [ ] **QA-01**: **Unit tests** (pytest) for `metrics.py` **structural load** path: mocked Neo4j session / result records so `get_structural_load_snapshot` (or equivalent public surface) is exercised without a live database; asserts stable shape for empty and non-empty graph fixtures.
- [ ] **QA-02**: **Unit tests** for `reconcile.py` **scan** logic (and any small pure helpers used for merge decisions) with **mocked** driver/session — no accidental writes; cover at least empty graph and a minimal duplicate-name fixture if feasible without integration DB.

### Open source & docs

- [ ] **DOC-01**: Repository root **LICENSE** (e.g. MIT) chosen and committed; **README** license section updated from placeholder to match; optional **CONTRIBUTING.md** stub only if it adds real value (not boilerplate noise).

### Dependencies & operator polish

- [ ] **PERF-01**: Address **`fuzzywuzzy` / Levenshtein** runtime warning: add optional **`python-Levenshtein`** (or documented alternative) in `pyproject.toml` / lockfile where appropriate, and note in README or reconcile section.

## Deferred (post–v1.1)

- **SENT-01**: Optional sentiment or subtext on edges — only if grounded in `source_quote` and secondary to structural metrics (`strategy.md`).
- **CI-01**: GitHub Actions (lint + tests) — optional follow-on once QA-01/02 exist.

## Out of scope (v1.1)

- **STACK-01**: Migrating off Neo4j, Streamlit, or the current LLM extraction stack.
- **VIBE-01**: Scoring “feel” without graph-level evidence.

## Traceability

| REQ-ID   | Phase | Status        |
|----------|-------|---------------|
| OUT-01   | 8     | Done (2026-04-03) |
| FLOW-01  | 9     | Done (2026-04-03) |
| DEMO-01  | 10    | Done (2026-04-03) |
| QA-01    | 5     | Not started   |
| QA-02    | 5     | Not started   |
| DOC-01   | 6     | Not started   |
| PERF-01  | 7     | Not started   |

### v1.0 (complete)

| REQ-ID    | Phase | Status           |
|-----------|-------|------------------|
| CONFIG-01 | 1     | Done (2026-04-03) |
| GEN-01    | 1     | Done (2026-04-03) |
| REL-01    | 2     | Done (2026-04-03) |
| REC-01    | 3     | Done (2026-04-03) |
| MET-01    | 4     | Done (2026-04-04) |

*Aligned with `.planning/ROADMAP.md`.*
