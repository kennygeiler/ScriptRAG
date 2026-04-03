# AGENTS.md — working in this repository

## Read first

1. **`strategy.md`** — Architecture, metric definitions, Streamlit app behavior, strict rules for changes. **`Telemetry.md`** — pipeline **`telemetry_version`** rubric and efficiency phase results log.
2. **`MEMORY.md`** — Short current-state snapshot (tabs, metrics, pipeline).
3. **`.cursorrules`** — Cursor-local summary; should stay consistent with `strategy.md`.

## Conventions

- **Package manager:** `uv` — `uv sync`, `uv run python …`, `uv run streamlit run app.py`.
- **Secrets:** Never commit `.env`. Use `.env.example` for variable names only.
- **Cypher:** Parameterized queries only; no string-built queries from user input.
- **Evidence:** Narrative edges in extracted data must carry verbatim `source_quote` from the script.
- **Scope:** Minimal diffs; match existing style in `app.py`, `metrics.py`, `neo4j_loader.py`.

## High-signal files

| Area | Files |
|------|--------|
| Sample scripts | `samples/` (`samples/README.md`); root **README** demo walkthrough |
| Optional tools | `tools/` (`tools/README.md`) — Neo4j QA exports, producer notes helper |
| Graph load | `neo4j_loader.py`, `schema.py` |
| Analytics | `metrics.py` |
| UI | `app.py`, `cleanup_review.py`, `pipeline_runs.py`, `reconcile.py`, `data_out.py` |
| ETL engine | `etl_core/graph_engine.py` (+ `etl_core/audit_policy.py`, `etl_core/state.py`, `etl_core/telemetry.py` — per-stage **extract/fix/audit** token + $ buckets), `domains/screenplay/adapter.py`, `domains/screenplay/auditors.py`, `domains/screenplay/audit_patch.py`, `domains/screenplay/audit_pipeline.py` — semantic audit **one pass**; gated **auto-apply** + HITL **warnings** (no `audit_fixer` loop) |
| Extract | `ingest.py` (`extract_scenes`, `run_single_scene_extraction`, `SceneResult` + `audit_decisions`), `extraction_graph.py`, `lexicon.py`, `parser.py` |

## When you finish a milestone

Update **`strategy.md`** (§3 progress, §4–§5 if metrics or UI changed), then **`MEMORY.md`** / **`.cursorrules`** if the snapshot drifted. GSD planning: **`.planning/PROJECT.md`**, **`.planning/ROADMAP.md`**, **`.planning/MILESTONES.md`** (active milestone **v1.1**).
