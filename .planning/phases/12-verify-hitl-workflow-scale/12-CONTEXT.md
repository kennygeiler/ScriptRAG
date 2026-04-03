# Phase 12 — Verify HITL workflow scale (HITL-02)

**Status:** Complete (2026-04-03) — see `12-01-PLAN.md` / `12-01-SUMMARY.md`.

## Shipped

- Filter by check type; order scenes (asc/desc, fewest/most warnings); sort cards within scene.
- Bulk Approve for visible `duplicate_relationship` warnings (whole extract + per-scene), each with confirmation checkbox.

## Dependencies

- Phase 11 (evidence cards).

## Risks (mitigated)

- Repeated merge for the same tuple at load: second `apply` pass is a no-op when the graph already has one row.
