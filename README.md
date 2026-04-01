# Narrative MRI

> Stop guessing if your script works. Measure its physics.

**Narrative MRI** is a GraphRAG-style pipeline for screenplays: Final Draft → validated JSON → **Neo4j** → a **Streamlit** dashboard. It surfaces structural signals—**pacing (momentum)**, **character agency over acts**, and **long-horizon props**—with evidence on edges as verbatim **`source_quote`** text.

**Authoritative detail:** [`strategy.md`](strategy.md) (architecture, metric definitions, AI rules). **Compact snapshot:** [`MEMORY.md`](MEMORY.md). **For coding agents:** [`AGENTS.md`](AGENTS.md).

**Remote:** [github.com/kennygeiler/GraphRAG](https://github.com/kennygeiler/GraphRAG) (private by default—adjust visibility in GitHub settings if you open-source it).

## Philosophy

Coverage is often subjective. Here, a screenplay is modeled as **typed relationships** among characters, locations, and props per scene. Metrics are reproducible from the graph, not from vibes alone.

## Stack

| Layer | Choice |
|--------|--------|
| Extraction | Claude via [`instructor`](https://github.com/jxnl/instructor) + Pydantic (`schema.py`) |
| Graph | [Neo4j](https://neo4j.com/) |
| Runtime | Python 3.12 + [`uv`](https://github.com/astral-sh/uv) |
| UI | [Streamlit](https://streamlit.io/) + [Plotly](https://plotly.com/python/) |

## Dashboard: Narrative Timeline Analyzer (`app.py`)

Wide-layout Streamlit app. Main analytics live under **Narrative Timeline**:

1. **Narrative momentum** — Per-scene **heat** = in-scene `CONFLICTS_WITH / (INTERACTS_WITH + CONFLICTS_WITH)` among co-present entities; **3-scene rolling average**; area fill; dashed markers at **Act 2 / Act 3** starts (derived from Neo4j).
2. **The Payoff Matrix (Long-Term Plot Devices)** — Props whose first on-screen intro and last narrative use are separated by more than **10** scene numbers (filters short-loop noise).
3. **Power shift** — **Passivity index** (in-degree / total degree on `CONFLICTS_WITH` + `USES`, windowed by act) for the **top five** characters by interaction volume. **Act boundaries** are **equal thirds** of the `min..max(:Event.number)` span in the database (script-agnostic). **`st.warning`** if the protagonist (**Zev**, configurable in code) has **higher** passivity in Act 3 than in Act 1.

Other tabs: **Human-in-the-Loop** (`hitl.py`), **Ask the graph** (`agent.py`), **Pipeline Engine** (nuke / upload `.fdx` / staged `uv run` pipeline).

## Prerequisites

- `uv` — `uv sync` installs from `pyproject.toml` / `uv.lock` (`requirements.txt` is ancillary).
- Running **Neo4j**
- **Anthropic** API key (ingest)

Copy **`.env.example`** → **`.env`** and fill in secrets. **Never commit `.env`.**

```env
ANTHROPIC_API_KEY=sk-ant-...
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=...
```

Optional (tracing / QA): `LANGCHAIN_*` variables as in `.env.example`.

## Usage

```bash
uv sync

# 1) Parse Final Draft → raw_scenes.json
uv run python parser.py screenplay.fdx

# 2) Master lexicon from raw scenes
uv run python lexicon.py raw_scenes.json

# 3) Per-scene LLM extract → validated_graph.json (checkpointed; re-run to resume)
uv run python ingest.py

# 4) Load Neo4j from validated_graph.json
uv run python neo4j_loader.py

# 5) Dashboard
uv run streamlit run app.py
```

**Optional CLI** (`metrics.py`, `reconcile.py`) — see `strategy.md` §4 and `--help` on each script.

## Project layout

| Path | Role |
|------|------|
| `parser.py` | `.fdx` → `raw_scenes.json` |
| `lexicon.py` | `master_lexicon.json` / `lexicon.json` |
| `ingest.py` | Scene graphs → `validated_graph.json` |
| `neo4j_loader.py` | JSON → Neo4j |
| `metrics.py` | Cypher analytics (momentum, payoff props, passivity, heat, etc.) |
| `app.py` | Streamlit application |
| `hitl.py` | Draft vs Gold scene review |
| `agent.py` | LangChain Cypher QA |
| `schema.py` | Pydantic graph contract |
| `strategy.md` | Full project brain |
| `MEMORY.md` | Short memory snapshot |
| `AGENTS.md` | Instructions for AI assistants |

## License

Add a license (e.g. MIT) when you publish the repo.
