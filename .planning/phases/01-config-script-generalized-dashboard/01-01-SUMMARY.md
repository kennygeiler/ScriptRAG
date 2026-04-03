# Plan 01-01 Summary — CONFIG-01

**Completed:** 2026-04-03

## Delivered

- `metrics.py`: `ORDER BY tot DESC, id ASC` in `get_top_characters_by_interaction_count` (deterministic ties).
- `lead_resolution.py`: `top_characters_k()`, `resolve_primary_character_id()` (override vs rank-1 analysis).
- `.env.example`: `SCRIPTRAG_PRIMARY_LEAD_ID`, `SCRIPTRAG_TOP_CHARACTERS`.
- `app.py`: Removed `PROTAGONIST_ID` / `TOP_INTERACTION_CHARACTERS`; `_cached_top_characters(stamp, k)`, `_cached_primary_lead`, `_extra` includes resolved primary, `_primary_lead_regression_warning`, sidebar **Primary lead** expander.

## Verification

- No `PROTAGONIST_ID` assignment in `app.py`.
- `rg "ORDER BY tot DESC, id ASC" metrics.py` matches.

## REQ

- CONFIG-01
