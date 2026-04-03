# Testing Patterns

**Analysis Date:** 2026-04-03

## Test Framework

**Runner:**
- Not detected: no `pytest`, `unittest` test modules, `pytest.ini`, `tox.ini`, or `[tool.pytest.ini_options]` in `pyproject.toml`.
- `uv.lock` contains no pytest dependency.

**Assertion Library:**
- Not applicable until a runner is added.

**Run Commands:**
```bash
# Not configured — add dev deps and pytest, then e.g.:
uv add --dev pytest
uv run pytest -q
uv run pytest tests/ -v --tb=short   # after creating tests/
```

## Test File Organization

**Location:**
- No `tests/` directory or `test_*.py` / `*_test.py` files in the application tree.

**Naming:**
- When introducing tests, prefer `tests/test_<module>.py` and functions `test_<behavior>()` for pytest discovery.

**Structure:**
```
GraphRAG/
├── tests/
│   ├── conftest.py          # shared fixtures (Neo4j optional, mock env)
│   ├── test_parser.py       # pure FDX → JSON (no network)
│   ├── test_schema.py       # Pydantic validation / proof rules
│   └── test_metrics.py      # optional: integration with test Neo4j
```

## Test Structure

**Suite Organization:**
- Not present in codebase. Recommended pattern once pytest exists:

```python
import pytest

from schema import Relationship

def test_relationship_requires_source_quote():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        Relationship(
            source_id="alan",
            target_id="theater",
            type="LOCATED_IN",
        )
```

**Patterns:**
- **Setup / teardown:** Use fixtures for temp JSON paths and `monkeypatch` for `os.environ` instead of relying on real `.env` in CI.
- **Assertions:** Prefer `pytest.raises` for validation errors; use plain `assert` for pure data transforms.

## Mocking

**Framework:** Not in use; standard library `unittest.mock` or `pytest-mock` would be typical add-ons.

**Patterns:**
- **Anthropic / instructor:** Mock `extraction_llm.call_llm_with_usage` or patch `_ensure_clients` to avoid API keys in unit tests.
- **Neo4j:** Mock `neo4j.Driver` session `run().data()` return values for `metrics.py` queries, or use a dedicated test database with `NEO4J_*` env in integration jobs only.

**What to Mock:**
- External HTTP (Claude), Neo4j in fast unit tests, filesystem when testing `pipeline_state` writes if tests become flaky.

**What NOT to Mock:**
- Pydantic `model_validate` / pure functions in `parser.py`, `lexicon` string handling, and `cleanup_review` helpers that only use in-memory dicts.

## Fixtures and Factories

**Test Data:**
- Reuse small JSON fragments matching `raw_scenes.json` / `validated_graph.json` shapes from `README.md` and `strategy.md` examples; store under `tests/fixtures/` as needed.

**Location:**
- Not applicable until created.

## Coverage

**Requirements:** None enforced in repository.

**View Coverage:**
```bash
# After adding pytest + pytest-cov:
uv add --dev pytest-cov
uv run pytest --cov=. --cov-report=term-missing
```

## Test Types

**Unit Tests:**
- Highest value first: `parser.py` (XML → scenes), `schema.py` / `domains/screenplay/rules.py` (business rules), `cleanup_review.py` (warning merging), `neo4j_loader.py` `_dedupe_relationships` with dict inputs.

**Integration Tests:**
- Optional: run `neo4j_loader.load_entries` against a throwaway Neo4j instance with minimal graph JSON; run one scene through `ingest.extract_scenes` with mocked LLM.

**E2E Tests:**
- Not used; Streamlit `app.py` is normally exercised manually or with separate E2E tooling (not in repo).

## Common Patterns

**Async Testing:**
- Not applicable: codebase is synchronous except for driver/session context managers.

**Error Testing:**
- Align with existing runtime checks: env missing → script exits 1 (test via subprocess or refactor to inject config for testability); Pydantic → `pytest.raises(ValidationError)`.

## Manual / ad hoc verification

**Existing sanity check:**
- `schema.py` exposes `if __name__ == "__main__":` that asserts `Relationship` cannot be constructed without `source_quote` (prints then re-raises `ValidationError`). This is not automated CI.

```bash
uv run python schema.py   # expect ValidationError after message
```

---

*Testing analysis: 2026-04-03*
