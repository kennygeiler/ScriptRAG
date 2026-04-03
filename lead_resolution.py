"""Resolve primary lead character for dashboard regression and cohort sizing."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from neo4j import Driver

from metrics import get_top_characters_by_interaction_count


def top_characters_k() -> int:
    """Power-shift cohort size; default 5, clamped 1..50."""
    raw = os.environ.get("SCRIPTRAG_TOP_CHARACTERS", "").strip()
    if not raw:
        return 5
    try:
        return max(1, min(int(raw), 50))
    except ValueError:
        return 5


def resolve_primary_character_id(*, driver: Driver | None = None) -> str | None:
    """Primary lead snake_case id: env override if set, else rank-1 by interaction count."""
    override = os.environ.get("SCRIPTRAG_PRIMARY_LEAD_ID", "").strip()
    if override:
        return override
    rows = get_top_characters_by_interaction_count(1, driver=driver)
    if not rows:
        return None
    return str(rows[0]["id"])
