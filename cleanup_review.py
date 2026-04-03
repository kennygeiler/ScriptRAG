"""Plain-language summaries for Cleanup Review (corrections + warning locations)."""

from __future__ import annotations

import re
from typing import Any


def plain_english_fix_reason(reason: str) -> str:
    """Turn validator / fixer error text into a short human explanation."""
    if not reason or not reason.strip():
        return "The extraction did not pass automated checks; the model rewrote the graph."
    low = reason.lower()
    if "hallucinated quote" in low or "not found in scene text" in low:
        return (
            "At least one relationship cited script text that does not appear verbatim in the "
            "scene (or normalizes differently). Quotes must be copy-pasteable from the scene."
        )
    if "duplicate located_in" in low:
        return (
            "The same character was placed in more than one location in this scene. "
            "Only one LOCATED_IN edge per character is allowed."
        )
    if "dangling edge" in low:
        return (
            "A relationship pointed to a character, location, or prop id that was not listed "
            "in the scene's node list."
        )
    if "self-referencing edge" in low:
        return "A relationship had the same entity as both source and target, which is invalid."
    if "invalid target kind" in low or "invalid source kind" in low:
        return (
            "A relationship type was wired to the wrong kind of node "
            "(for example, LOCATED_IN must end at a Location)."
        )
    if "validation error" in low or "field required" in low:
        return "The JSON did not match the required schema (missing fields or wrong types)."
    if "1 validation error" in low or "validationerror" in low.replace(" ", ""):
        return "Pydantic schema validation failed on the extracted graph structure."
    # Audit-phase combined messages (free text)
    if len(reason) > 380:
        return reason[:380].rstrip() + "…"
    return reason


def summarize_graph_delta(before: dict[str, Any], after: dict[str, Any]) -> tuple[str, str]:
    """Compact before/after descriptions (not full JSON)."""
    def _shape(g: dict[str, Any]) -> tuple[dict[str, int], list[tuple[str, str, str]]]:
        nodes = g.get("nodes") if isinstance(g.get("nodes"), list) else []
        rels = g.get("relationships") if isinstance(g.get("relationships"), list) else []
        nk: dict[str, int] = {}
        for n in nodes:
            if not isinstance(n, dict):
                continue
            k = str(n.get("kind") or "?")
            nk[k] = nk.get(k, 0) + 1
        edges: list[tuple[str, str, str]] = []
        for r in rels:
            if not isinstance(r, dict):
                continue
            edges.append(
                (
                    str(r.get("type") or "?"),
                    str(r.get("source_id") or "?"),
                    str(r.get("target_id") or "?"),
                )
            )
        return nk, edges

    bn, br = _shape(before)
    an, ar = _shape(after)

    def _fmt_nodes(d: dict[str, int]) -> str:
        return ", ".join(f"{k}: {v}" for k, v in sorted(d.items())) or "(none)"

    before_lines = [
        f"**Nodes** — {_fmt_nodes(bn)}",
        f"**Relationships** — {len(br)} edge(s)",
    ]
    after_lines = [
        f"**Nodes** — {_fmt_nodes(an)}",
        f"**Relationships** — {len(ar)} edge(s)",
    ]

    bset, aset = set(br), set(ar)
    removed = sorted(bset - aset)
    added = sorted(aset - bset)
    if removed:
        before_lines.append("**Removed edges** (type, source → target):")
        for t, s, tid in removed[:12]:
            before_lines.append(f"- `{t}`: `{s}` → `{tid}`")
        if len(removed) > 12:
            before_lines.append(f"- … and {len(removed) - 12} more")
    if added:
        after_lines.append("**Added edges**:")
        for t, s, tid in added[:12]:
            after_lines.append(f"- `{t}`: `{s}` → `{tid}`")
        if len(added) > 12:
            after_lines.append(f"- … and {len(added) - 12} more")
    if not removed and not added and br == ar:
        before_lines.append("_Edge list unchanged; node or quote text may have been edited._")

    return "\n".join(before_lines), "\n".join(after_lines)


def warning_json_location(warning: dict[str, Any], entries: list[dict[str, Any]]) -> str:
    """Human-readable path into the extracted scene graph for a warning."""
    sn = warning.get("scene_number")
    check = str(warning.get("check", "unknown"))
    detail = str(warning.get("detail", ""))
    idx = warning.get("relationship_index")

    entry: dict[str, Any] | None = None
    if sn is not None:
        for e in entries:
            if not isinstance(e, dict):
                continue
            if int(e.get("scene_number") or -1) == int(sn):
                entry = e
                break
    graph = (entry or {}).get("graph") if entry else None
    if not isinstance(graph, dict):
        return f"Scene **{sn}** / `graph` — _scene not found in current extract_"

    base = f"Scene **{sn}**"

    if idx is not None and isinstance(graph.get("relationships"), list):
        rels = graph["relationships"]
        if 0 <= int(idx) < len(rels):
            r = rels[int(idx)]
            if isinstance(r, dict):
                return (
                    f"{base} → `graph.relationships[{idx}]` "
                    f"(`{r.get('type', '?')}`: `{r.get('source_id', '?')}` → `{r.get('target_id', '?')}`)"
                )
        return f"{base} → `graph.relationships` (index {idx} out of range)"

    if check == "lexicon_compliance":
        m = re.search(r"id='([^']+)'|id=([^\\s)]+)", detail)
        nid = (m.group(1) or m.group(2)).strip("'\"") if m else None
        nodes = graph.get("nodes") if isinstance(graph.get("nodes"), list) else []
        for i, n in enumerate(nodes):
            if isinstance(n, dict) and nid and str(n.get("id")) == nid:
                return f"{base} → `graph.nodes[{i}]` (id `{nid}`)"
        return f"{base} → `graph.nodes` — {detail[:120]}"

    if check == "duplicate_relationship":
        return f"{base} → `graph.relationships` — duplicate tuple in this scene"

    if check == "audit_skipped":
        return f"{base} — _LLM audit step failed; deterministic checks only_"

    if check in ("quote_fidelity", "completeness", "attribution"):
        if idx is not None and isinstance(graph.get("relationships"), list):
            return f"{base} → `graph.relationships[{idx}]` — **{check}**"
        return f"{base} → `graph` — **{check}**"

    return f"{base} → `graph` — **{check}**"
