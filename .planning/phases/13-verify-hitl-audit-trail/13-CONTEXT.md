# Phase 13 — Verify HITL audit trail (HITL-03)

**Status:** Not started — placeholder for planning.

## Intent

- On **Approve & Load**, offer download of **CSV/JSON** listing: scene, check, approve/decline/unset, timestamp, optional short note.
- Optional per-warning text field (“reason for decline”) stored only in export / session log (not Neo4j unless explicitly requested later).

## Dependencies

- Phase 11; optionally Phase 12 for consistent warning ordering in exports.
