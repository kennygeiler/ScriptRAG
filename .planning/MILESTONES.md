# Milestones — ScriptRAG (GSD)

## v1.0 — Brownfield hardening & operator surface (complete)

**Completed:** 2026-04-04  
**Phases:** 1–4 (see **Completed milestone v1.0** in `.planning/ROADMAP.md`, and phase dirs `01`–`04` under `.planning/phases/`).

**Shipped:**

- **CONFIG / GEN:** Analysis-derived primary lead + `SCRIPTRAG_PRIMARY_LEAD_ID` / `SCRIPTRAG_TOP_CHARACTERS`; script-agnostic operator copy (`lead_resolution.py`, `app.py`).
- **REL-01:** Empty / partial Neo4j and skewed query shapes do not crash Streamlit metric paths.
- **REC-01:** `reconcile.py` CLI (`--dry-run`, `--scope`) + Streamlit **Reconcile** tab; safe merge (APOC or manual rewire).
- **MET-01:** Structural load snapshot (`get_structural_load_snapshot`), Dashboard + `metrics.py --structural-load`.

---

## v1.1 — Quality, tests & open-source hygiene (active)

See `.planning/PROJECT.md` (**Current Milestone**), `.planning/REQUIREMENTS.md`, and `.planning/ROADMAP.md` (Phases 5+).
