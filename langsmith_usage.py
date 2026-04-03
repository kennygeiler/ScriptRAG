"""Aggregate token usage from LangSmith for a time window (optional)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from etl_core.telemetry import estimate_cost


def aggregate_langsmith_usage(
    start: datetime,
    end: datetime | None = None,
    *,
    project_name: str | None = None,
) -> tuple[int, float]:
    """
    Sum prompt + completion tokens from traced LLM runs in the project between start and end.

    Returns (total_tokens, estimated_cost_usd). Cost is estimated from per-run model metadata
    when available, else blended Sonnet pricing on total in/out splits.

    If LangSmith is not configured or the client fails, returns (0, 0.0).
    """
    end = end or datetime.now(timezone.utc)
    project = project_name or os.environ.get("LANGCHAIN_PROJECT", "scriptrag")
    api_key = os.environ.get("LANGCHAIN_API_KEY")
    tracing = os.environ.get("LANGCHAIN_TRACING_V2", "").lower() in ("true", "1", "yes")
    if not api_key or not tracing:
        return 0, 0.0

    try:
        from langsmith import Client
    except ImportError:
        return 0, 0.0

    try:
        client = Client(api_key=api_key)
    except Exception:
        return 0, 0.0

    total_in = 0
    total_out = 0
    cost_parts: list[tuple[str, int, int]] = []

    try:
        for run in client.list_runs(
            project_name=project,
            start_time=start,
            end_time=end,
            run_type="llm",
            limit=20_000,
        ):
            pt = int(getattr(run, "prompt_tokens", None) or 0)
            ct = int(getattr(run, "completion_tokens", None) or 0)
            tt = getattr(run, "total_tokens", None)
            if tt is not None and int(tt) > 0 and pt == 0 and ct == 0:
                # Some providers only populate total_tokens
                half = int(tt) // 2
                pt, ct = half, int(tt) - half
            total_in += pt
            total_out += ct
            model = _extract_model_name(run)
            if pt or ct:
                cost_parts.append((model, pt, ct))
    except Exception:
        return 0, 0.0

    tokens = total_in + total_out
    if not cost_parts:
        return tokens, 0.0

    cost = 0.0
    for model, pi, co in cost_parts:
        cost += estimate_cost(model, pi, co)
    return tokens, round(cost, 6)


def _extract_model_name(run: Any) -> str:
    extra = getattr(run, "extra", None) or {}
    if isinstance(extra, dict):
        md = extra.get("metadata") or {}
        if isinstance(md, dict):
            for key in ("ls_model_name", "model_name", "model"):
                v = md.get(key)
                if isinstance(v, str) and v:
                    return v
    kwargs = getattr(run, "serialized", None) or {}
    if isinstance(kwargs, dict):
        k = kwargs.get("kwargs") or {}
        if isinstance(k, dict) and isinstance(k.get("model"), str):
            return k["model"]
    return "claude-sonnet-4-6"
