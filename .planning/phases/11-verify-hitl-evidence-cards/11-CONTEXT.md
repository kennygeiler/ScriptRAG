# Phase 11 — Verify HITL evidence cards (HITL-01)

**Milestone:** v1.3  
**Requirement:** HITL-01

## Problem

Verify cards showed pipeline text and JSON location but not **each duplicate row / targeted edge** or a concise **Approve outcome**, slowing HITL and increasing mis-clicks.

## Approach

Pure helpers in `cleanup_review.py` + Verify UI grouping and expanders; no Neo4j or pipeline schema changes.

## Plans

- `11-01-PLAN.md` — executed; see `11-01-SUMMARY.md`.
