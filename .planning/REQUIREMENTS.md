# Requirements — ScriptRAG (v1.1 GSD track)

Requirements for the **current planning milestone**: automated tests for critical analytics/reconcile paths, explicit open-source licensing, and small dependency/operator polish. v1.0 REQ-IDs remain satisfied; see `.planning/MILESTONES.md` and the traceability table at the end for v1.0 history.

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
