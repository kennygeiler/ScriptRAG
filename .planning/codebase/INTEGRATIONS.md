# External Integrations

**Analysis Date:** 2026-04-03

## APIs & External Services

**Anthropic (Claude):**
- Screenplay extraction, lexicon generation, validation fix passes, and auditor agents — direct SDK in `extraction_llm.py`, `lexicon.py`, domain auditors under `domains/screenplay/`
- SDK/Client: `anthropic` package; structured calls via `instructor.from_anthropic`
- Auth: `ANTHROPIC_API_KEY` (see `.env.example`)

**Anthropic via LangChain (subset):**
- Natural-language answers over the graph — `ChatAnthropic` in `agent.py` (same API key as above, consumed by LangChain)

**LangSmith (optional):**
- Trace UI for LangChain/LangGraph when enabled
- Config: `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_ENDPOINT`, `LANGCHAIN_PROJECT` (defaults set in `etl_core/config.py` when tracing is on)
- Bootstrap: `enable_langsmith()` in `etl_core/config.py`, called from `ingest.py` before pipeline runs

## Data Storage

**Databases:**
- Neo4j (property graph) — script graph (`Character`, `Location`, `Prop`, `Event`, narrative relationships), pipeline efficiency as `:PipelineRun` nodes (`pipeline_runs.py`, `neo4j_loader.py`, `metrics.py`)
- Connection: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` (`.env.example`)
- Client: official `neo4j` Python driver; LangChain `Neo4jGraph` wraps connectivity for QA in `agent.py`
- ORM: Not used — Cypher via parameterized queries in `metrics.py`, `neo4j_loader.py`, etc.

**File Storage:**
- Local filesystem — uploads, intermediate JSON (`parser.py`, `ingest.py`, `pipeline_state.py` patterns per app flow)
- Optional durable directory — `PERSISTENT_DATA_DIR` for deployments with mounted volumes (`docker-entrypoint.sh`, `docker-compose.yml`, `render.yaml`, `.env.example` comments)

**Caching:**
- None as a dedicated service; Streamlit session state and in-process patterns only

## Authentication & Identity

**Auth Provider:**
- Not applicable for end users — Streamlit app is not wired to OAuth or session login in codebase
- Service-to-service: API keys and DB credentials via environment variables only

## Monitoring & Observability

**Error Tracking:**
- No Sentry/Rollbar-style integration detected

**Logs:**
- Standard output / Streamlit; optional LangSmith traces for ETL when configured

## CI/CD & Deployment

**Hosting:**
- Render — Blueprint `render.yaml` (Docker web service, health check `/_stcore/health`, persistent disk optional)
- Generic Docker — `Dockerfile` suitable for Fly/Railway-style `PORT` usage (per `README.md`)

**CI Pipeline:**
- Not detected — no `.github/workflows` in repository

## Environment Configuration

**Required env vars:**
- `ANTHROPIC_API_KEY` — extraction and QA LLM calls
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` — graph persistence and dashboard queries

**Optional env vars:**
- `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_ENDPOINT`, `LANGCHAIN_PROJECT` — LangSmith
- `PERSISTENT_DATA_DIR` — writable path for durable files on disk-backed hosts
- `DISABLE_PIPELINE` — when truthy, hides pipeline UI (`app.py`)

**Secrets location:**
- Local `.env` (gitignored); production secret sync per host (e.g. Render `sync: false` in `render.yaml`)

## Webhooks & Callbacks

**Incoming:**
- None — no HTTP callback endpoints defined for external systems

**Outgoing:**
- None — no registered webhooks; LLM and DB are request/response from the app process

---

*Integration audit: 2026-04-03*
