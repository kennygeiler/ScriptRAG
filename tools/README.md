# Tools

Optional scripts for Neo4j QA and overlays. Run from the **repository root** so outputs land next to other artifacts:

```bash
uv run python tools/debug_export.py    # → graph_qa_dump.json
uv run python tools/qa_entities.py     # → data_health_report.json
```

`producer_notes.py` is a small library (imports `metrics.get_driver`); use from the repo root with `PYTHONPATH=.` or run snippets that import it after `cd` to the project root.

Requires the same **`NEO4J_*`** (and `.env`) as the main app.
