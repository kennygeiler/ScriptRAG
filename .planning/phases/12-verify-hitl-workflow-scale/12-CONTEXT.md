# Phase 12 — Verify HITL workflow scale (HITL-02)

**Status:** Not started — placeholder for planning.

## Intent

- Filter and/or sort warnings (by check type, scene, severity).
- Optional **bulk Approve** for `duplicate_relationship` within a scene (or whole extract) with an explicit confirmation step.

## Dependencies

- Phase 11 (evidence cards) complete.

## Risks

- Bulk approve must not double-apply edits when multiple warnings reference the same tuple; confirm interaction with `apply_approved_warning_edits` ordering.
