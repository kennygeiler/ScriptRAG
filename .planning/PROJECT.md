# ScriptRAG (GraphRAG)

## What This Is

**ScriptRAG** is a GraphRAG system for screenplays: Final Draft (`.fdx`) is parsed into JSON, a self-healing LLM pipeline extracts a validated scene graph (Pydantic + instructor) with **verbatim `source_quote`** on narrative edges, and **Neo4j** stores `Character`, `Location`, `Prop`, and `Event` nodes with structural and narrative relationships. A **Streamlit** app runs the pipeline, cleanup review, **reconciliation** (`reconcile.py`), efficiency tracking, structural metrics dashboards (including **structural load** MET-01), and natural-language graph investigation. **Primary lead** and cohort sizing for role-dependent charts come from graph analysis with optional **`SCRIPTRAG_*`** env overrides (`lead_resolution.py`).

**Audience:** Writers, producers, and developers analyzing narrative “physics” (agency, friction, props, conflict structure)—not vibes without evidence.

## Core Value

End-to-end, **evidence-backed** structural analysis of a screenplay in a queryable graph—with a working pipeline from upload → validated extraction → Neo4j → metrics and investigation.

## Current Milestone: v1.1 — Quality, tests & open-source hygiene

**Goal:** Add **automated tests** for critical `metrics` / `reconcile` surfaces, ship an explicit **LICENSE** and aligned README legal copy, and clear **fuzzy matching** dependency warnings for operators.

**Target features:**

- Pytest coverage with **mocked Neo4j** for structural load and reconcile scan paths (REQ **QA-01**, **QA-02**).
- Root **LICENSE** + README license section (**DOC-01**).
- Optional **`python-Levenshtein`** (or equivalent) to satisfy `fuzzywuzzy` performance path + docs (**PERF-01**).

## Requirements

### Validated

- ✓ **FDX → JSON parsing** with stable scene numbering — existing (`parser.py`)
- ✓ **Lexicon + per-scene extraction** with self-healing LangGraph ETL (`etl_core`, `ingest.py`, `domains/screenplay/`) — existing
- ✓ **Neo4j load** with merge semantics and `source_quote` on narrative rels (`neo4j_loader.py`) — existing
- ✓ **Metrics layer** (passivity, scene heat, momentum, payoff props, act buckets, power shift, structural load MET-01, etc.) — existing (`metrics.py`)
- ✓ **Streamlit product** — Pipeline, Cleanup Review, **Reconcile**, Efficiency Tracking, Dashboard, Investigate (`app.py`, `cleanup_review.py`, `reconcile.py`, `agent.py`, `pipeline_runs.py`, `lead_resolution.py`) — existing
- ✓ **Pipeline run telemetry** as `:PipelineRun` nodes — existing
- ✓ **Ask-the-graph** NL → Cypher path — existing (`agent.py`)
- ✓ **Analysis-derived primary lead + env overrides** — `lead_resolution.py`, `SCRIPTRAG_PRIMARY_LEAD_ID` / `SCRIPTRAG_TOP_CHARACTERS`, Dashboard regression + sidebar (Phase 1, 2026-04-03).
- ✓ **Script-agnostic operator copy** — no hardcoded production character IDs in `app.py` UI strings; docs aligned (`MEMORY.md`, `strategy.md`).
- ✓ **Empty / partial graph hardening (REL-01)** — explicit empty states and safe metric paths when Neo4j is missing or incomplete (Phase 2, 2026-04-03).
- ✓ **Reconciliation for operators (REC-01)** — `reconcile.py` CLI + Streamlit tab; documented merge semantics (Phase 3, 2026-04-03).
- ✓ **Structural load / production signal (MET-01)** — `get_structural_load_snapshot`, Dashboard + CLI (Phase 4, 2026-04-04).

### Active

- [ ] **QA-01 / QA-02** — Unit tests for structural load and reconcile scan (mocked driver); see `.planning/REQUIREMENTS.md`.
- [ ] **DOC-01** — LICENSE + README license alignment.
- [ ] **PERF-01** — Optional Levenshtein acceleration for fuzzy reconcile; document in README.

### Out of Scope

- **Sentiment / subtext on edges** unless strictly grounded in `source_quote` and secondary to structural metrics — exploratory future phase (`strategy.md` §3).
- **Replacing** the core stack (Neo4j, Streamlit, Anthropic/instructor) — not this milestone.
- **Vibe-only scoring** without graph evidence — conflicts with project philosophy.

## Context

- **Authoritative product doc:** `strategy.md` (metrics definitions, dashboard map, AI rules). **Short mirror:** `MEMORY.md`, `.cursorrules`, `AGENTS.md`.
- **Code layout:** Flat Python modules at repo root; generic ETL in `etl_core/`; screenplay domain in `domains/screenplay/`. See `.planning/codebase/ARCHITECTURE.md` and `STRUCTURE.md`.
- **Package manager:** `uv` (`uv sync`, `uv run`).
- **Secrets:** `.env` only; template `.env.example`.
- **GSD:** Codebase mapped under `.planning/codebase/`; this file initializes the GSD project track for forward work aligned with `strategy.md`.

## Constraints

- **Tech:** Python 3.12, Neo4j, Streamlit, Plotly, parameterized Cypher only for user-facing query paths.
- **Evidence:** Narrative edges must retain verbatim `source_quote` from the script.
- **Documentation:** On major milestones, update `strategy.md` first, then mirrors—per repo rules.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Brownfield GSD init without parallel web research | Domain and stack already documented in `strategy.md` and `.planning/codebase/*` | Applied for v1.0 |
| Coarse roadmap granularity | Few broad phases for solo/small-team execution | Applied v1.0; v1.1 continues phase numbering at 5 |
| Track planning docs in git | `commit_docs: true` in GSD config | Applied |
| v1.1 scope: tests before CI | QA-01/02 justify later CI-01 | — Open |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):

1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):

1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-03 — new milestone v1.1 started (`/gsd-new-milestone`); v1.0 archived in `.planning/MILESTONES.md`.*
