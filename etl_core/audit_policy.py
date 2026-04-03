"""Thresholds and flags for semantic audit interpretation (P0–P2).

P0: logging + gates only. P1+: auto-apply when all gates pass.
"""

from __future__ import annotations

# Minimum model-reported confidence [0, 1] to consider auto-apply (P1+).
AUTO_APPLY_MIN_CONFIDENCE = 0.6

# Auditor `check` values allowed for unattended graph edits.
AUTO_APPLY_CHECKS_PHASE1: frozenset[str] = frozenset({"quote_fidelity", "attribution"})

# Completeness "add edge" auto-apply (P2): requires substring quote + id gates.
AUTO_APPLY_COMPLETENESS_ADD = True

# If True, run auto-apply after gates (P1+). False = P0 (log only).
AUTO_APPLY_ENABLED = True

# Risk flag strings produced by gates; any match blocks auto-apply.
RISK_FLAGS_BLOCK_AUTO: frozenset[str] = frozenset(
    {
        "quote_not_in_scene_text",
        "invalid_relationship_type",
        "relationship_index_out_of_range",
        "patch_ids_not_in_graph",
        "patch_ids_not_in_lexicon",
        "ambiguous_patch",
        "pydantic_or_rules_failed_after_apply",
    }
)
