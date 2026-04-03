"""Post-audit interpretation: gates, optional auto-apply, HITL warnings, JSONL log."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from etl_core import audit_policy as ap
from domains.screenplay.audit_patch import apply_finding_patch, gates_for_finding, validate_graph_after_patch

_AUDIT_DECISIONS_LOG = Path(__file__).resolve().parent.parent.parent / "audit_decisions.jsonl"


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_audit_decisions_jsonl(rows: list[dict[str, Any]], path: Path | None = None) -> None:
    p = path or _AUDIT_DECISIONS_LOG
    if not rows:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _hitl_warning_from_finding(finding: dict[str, Any], doc_id: Any, finding_index: int) -> dict[str, Any]:
    w = dict(finding)
    w.setdefault("check", str(finding.get("check") or "unknown"))
    w["severity"] = str(finding.get("severity") or "warning")
    w["scene_number"] = doc_id
    w["requires_hitl"] = True
    w["audit_finding_index"] = finding_index
    return w


def _allowed_auto_mapping(check: str, md: str) -> bool:
    if not ap.AUTO_APPLY_ENABLED:
        return False
    if check == "completeness" and md == "propose_add":
        return ap.AUTO_APPLY_COMPLETENESS_ADD
    if check not in ap.AUTO_APPLY_CHECKS_PHASE1:
        return False
    if check == "quote_fidelity" and md in ("propose_retype", "propose_remove"):
        return True
    if check == "attribution" and md in ("propose_swap", "propose_retype", "propose_remove"):
        return True
    return False


def process_semantic_audit(
    doc_id: Any,
    graph_json: dict[str, Any],
    raw_text: str,
    lexicon_ids: frozenset[str],
    findings: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Returns ``(updated_graph, audit_decisions, hitl_warnings, self_heal_trail_entries)``.

    *self_heal_trail_entries* use ``node``: ``auditor_auto_apply`` for Pipeline corrections.
    """
    g = graph_json
    decisions: list[dict[str, Any]] = []
    hitl: list[dict[str, Any]] = []
    heal: list[dict[str, Any]] = []

    for i, finding in enumerate(findings):
        check = str(finding.get("check") or "")
        md = str(finding.get("mapping_decision") or "defer_human")
        try:
            conf = float(finding.get("confidence", 0.0) or 0.0)
        except (TypeError, ValueError):
            conf = 0.0
        conf = max(0.0, min(1.0, conf))

        risk_from_model = finding.get("risk_flags") or []
        if not isinstance(risk_from_model, list):
            risk_from_model = []

        gate_risk, gate_notes = gates_for_finding(g, raw_text, lexicon_ids, finding)
        merged_risk = list(dict.fromkeys([*risk_from_model, *gate_risk]))

        try_auto = _allowed_auto_mapping(check, md)
        if try_auto:
            if conf < ap.AUTO_APPLY_MIN_CONFIDENCE:
                try_auto = False
            elif gate_risk:
                try_auto = False
            elif any(rf in ap.RISK_FLAGS_BLOCK_AUTO for rf in risk_from_model):
                try_auto = False

        action = "deferred_hitl"
        applied = False
        graph_before = deepcopy(g)

        if try_auto:
            new_g = apply_finding_patch(g, finding)
            if new_g is None:
                try_auto = False
                merged_risk.append("ambiguous_patch")
                gate_notes.append("apply_finding_patch returned None.")
            else:
                ok, val_errs = validate_graph_after_patch(new_g, raw_text, lexicon_ids)
                if ok:
                    g = new_g
                    applied = True
                    action = "auto_applied"
                    heal.append({
                        "ts": _ts(),
                        "doc_id": doc_id,
                        "node": "auditor_auto_apply",
                        "detail": "semantic_patch_applied",
                        "finding_index": i,
                        "check": check,
                        "mapping_decision": md,
                        "confidence": conf,
                        "before": graph_before,
                        "after": deepcopy(g),
                        "reason": "; ".join(gate_notes) if gate_notes else str(finding.get("detail") or ""),
                    })
                else:
                    merged_risk.append("pydantic_or_rules_failed_after_apply")
                    gate_notes.extend(val_errs[:5])

        if not applied:
            action = "deferred_hitl"
            hitl.append(_hitl_warning_from_finding(finding, doc_id, i))

        decisions.append({
            "ts": _ts(),
            "doc_id": doc_id,
            "finding_index": i,
            "check": check,
            "mapping_decision": md,
            "confidence": conf,
            "risk_flags": merged_risk,
            "gate_errors": gate_notes,
            "action": action,
            "detail": finding.get("detail"),
        })

    append_audit_decisions_jsonl(decisions)
    return g, decisions, hitl, heal
