# Summary 08-01 — Data out surface (OUT-01)

**Completed:** 2026-04-03  
**Requirement:** OUT-01

## Delivered

- **`data_out.py`:** `graph_schema_card_markdown`, `get_label_counts`, `get_rel_type_counts`, `rows_narrative_edges` / `rows_characters` / `rows_events`, `DEMO_QUERY_SPECS` + `run_demo_query` — all Cypher parameterized where dynamic lists are used (`$types` from `NARRATIVE_REL_TYPES`).
- **`app.py`:** New tab **Data out** after **Reconcile**; `@st.cache_data` helpers keyed on `_neo4j_dashboard_cache_stamp()`; CSV download buttons; Reconcile caption = optional post-load hygiene.
- **Docs:** `strategy.md` §5/§6/§8, `README.md`, `MEMORY.md`, `AGENTS.md`, `.cursorrules`.

## Verification notes

- Empty graph: expect info + empty downloads (disabled).
- Loaded graph: label/rel tables, recipe query results, non-empty CSVs.
- Re-run **Reload metrics** after external Neo4j edits.

## Follow-ups (not this plan)

- Phase 9 **FLOW-01** — Cleanup/Efficiency copy.
- Phase 10 **DEMO-01** — optional tab layout flag.
- Optional: single-click **validated_graph.json** download from UI.
