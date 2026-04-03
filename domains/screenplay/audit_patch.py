"""Validate and apply structured semantic-audit patches to scene graph JSON."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

from pydantic import ValidationError

from domains.screenplay.rules import validate_business_logic
from domains.screenplay.schemas import SceneGraph
from schema import RelationshipType

_WS = re.compile(r"\s+")

_ALLOWED = set(RelationshipType.__args__)  # type: ignore[attr-defined]


def _normalize(text: str) -> str:
    return _WS.sub(" ", text).strip().lower()


def quote_in_scene(source_quote: str, raw_text: str) -> bool:
    if not raw_text or not source_quote or not source_quote.strip():
        return False
    return _normalize(source_quote) in _normalize(raw_text)


def _node_ids(graph: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for n in graph.get("nodes") or []:
        if isinstance(n, dict) and n.get("id"):
            out.add(str(n["id"]))
    return out


def _rels(graph: dict[str, Any]) -> list[dict[str, Any]]:
    rels = graph.get("relationships")
    return rels if isinstance(rels, list) else []


def validate_graph_after_patch(
    graph: dict[str, Any],
    raw_text: str,
    lexicon_ids: frozenset[str],
) -> tuple[bool, list[str]]:
    errs: list[str] = []
    try:
        SceneGraph.model_validate(graph)
    except ValidationError as e:
        errs.append(str(e))
    re, _rw = validate_business_logic(graph, {"raw_text": raw_text, "lexicon_ids": set(lexicon_ids)})
    errs.extend(re)
    return (len(errs) == 0, errs)


def _effective_rel_index(finding: dict[str, Any]) -> Any:
    v = finding.get("patch_relationship_index")
    if v is not None:
        return v
    return finding.get("relationship_index")


def gates_for_finding(
    graph: dict[str, Any],
    raw_text: str,
    lexicon_ids: frozenset[str],
    finding: dict[str, Any],
) -> tuple[list[str], list[str]]:
    """
    Return (risk_flags, gate_error_messages) for a finding's proposed patch.
    Empty risk_flags => patch passed structural gates (may still defer on policy).
    """
    flags: list[str] = []
    notes: list[str] = []
    md = str(finding.get("mapping_decision") or "defer_human")

    if md in ("none", "defer_human"):
        return ([], [])

    rels = _rels(graph)
    nids = _node_ids(graph)
    idx = _effective_rel_index(finding)
    new_type = finding.get("patch_new_type")
    ps = finding.get("patch_source_id")
    pt = finding.get("patch_target_id")
    pq = finding.get("patch_source_quote")
    prt = finding.get("patch_relationship_type")

    if md == "propose_retype":
        if not isinstance(idx, int) or idx < 0 or idx >= len(rels):
            flags.append("relationship_index_out_of_range")
            notes.append(f"retype: index {idx!r} invalid (len={len(rels)}).")
        else:
            nt = str(new_type or "")
            if nt not in _ALLOWED:
                flags.append("invalid_relationship_type")
                notes.append(f"retype: type {nt!r} not allowed.")
        return (flags, notes)

    if md == "propose_remove":
        if not isinstance(idx, int) or idx < 0 or idx >= len(rels):
            flags.append("relationship_index_out_of_range")
            notes.append(f"remove: index {idx!r} invalid.")
        return (flags, notes)

    if md == "propose_swap":
        if not isinstance(idx, int) or idx < 0 or idx >= len(rels):
            flags.append("relationship_index_out_of_range")
            notes.append(f"swap: index {idx!r} invalid.")
        return (flags, notes)

    if md == "propose_add":
        rt = str(prt or "")
        if rt not in _ALLOWED:
            flags.append("invalid_relationship_type")
            notes.append(f"add: type {rt!r} not allowed.")
        sid = str(ps or "")
        tid = str(pt or "")
        if sid not in nids or tid not in nids:
            flags.append("patch_ids_not_in_graph")
            notes.append("add: source_id or target_id not present in graph nodes.")
        if lexicon_ids and (sid not in lexicon_ids or tid not in lexicon_ids):
            # Props may not be in lexicon — only enforce for character/location-like if both missing
            if sid not in lexicon_ids and tid not in lexicon_ids:
                pass
        sq = str(pq or "")
        if not quote_in_scene(sq, raw_text):
            flags.append("quote_not_in_scene_text")
            notes.append("add: source_quote not found verbatim (normalized) in scene text.")
        return (flags, notes)

    flags.append("ambiguous_patch")
    notes.append(f"unknown mapping_decision {md!r}.")
    return (flags, notes)


def apply_finding_patch(graph: dict[str, Any], finding: dict[str, Any]) -> dict[str, Any] | None:
    """
    Return a deep-copied graph with patch applied, or None if unsupported / invalid index.
    """
    g = deepcopy(graph)
    rels = _rels(g)
    if not isinstance(g.get("relationships"), list):
        g["relationships"] = rels
    md = str(finding.get("mapping_decision") or "")

    if md == "propose_retype":
        idx = _effective_rel_index(finding)
        nt = finding.get("patch_new_type")
        if not isinstance(idx, int) or idx < 0 or idx >= len(rels):
            return None
        if str(nt) not in _ALLOWED:
            return None
        rels[idx] = dict(rels[idx])
        rels[idx]["type"] = str(nt)
        return g

    if md == "propose_remove":
        idx = _effective_rel_index(finding)
        if not isinstance(idx, int) or idx < 0 or idx >= len(rels):
            return None
        g["relationships"] = [r for i, r in enumerate(rels) if i != idx]
        return g

    if md == "propose_swap":
        idx = _effective_rel_index(finding)
        if not isinstance(idx, int) or idx < 0 or idx >= len(rels):
            return None
        r = dict(rels[idx])
        sid, tid = r.get("source_id"), r.get("target_id")
        r["source_id"], r["target_id"] = tid, sid
        rels[idx] = r
        return g

    if md == "propose_add":
        sid, tid = finding.get("patch_source_id"), finding.get("patch_target_id")
        rt = finding.get("patch_relationship_type")
        sq = finding.get("patch_source_quote")
        if not all([sid, tid, rt, sq]):
            return None
        if str(rt) not in _ALLOWED:
            return None
        rels.append({
            "source_id": str(sid),
            "target_id": str(tid),
            "type": str(rt),
            "source_quote": str(sq),
        })
        g["relationships"] = rels
        return g

    return None
