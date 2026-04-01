# Project memory (compact)

**Last aligned:** March 2026. For full detail use **`strategy.md`**.

## What this is

Screenplay **GraphRAG**: `.fdx` → JSON → **Neo4j** (`Character`, `Location`, `Prop`, `Event` + `IN_SCENE` + narrative rels with `source_quote`). **Streamlit** app = **Narrative Timeline Analyzer** + HITL + graph chat + pipeline UI.

## Dashboard tabs (`app.py`)

| Tab | Purpose |
|-----|---------|
| **Narrative Timeline** | Momentum line (rolling heat), Payoff Matrix (long-gap props), Power shift (top 5 × 3 acts), protagonist regression warning |
| **Human-in-the-Loop** | Non-`VERIFIED` scenes → edit graph → approve |
| **Ask the graph** | Natural language → Cypher (`agent.py`) |
| **Pipeline Engine** | Wipe DB/JSONs, upload `.fdx`, run parser → lexicon → ingest → loader with logs |

## Act structure (dynamic)

From Neo4j: **`get_script_act_bounds`** in `metrics.py` — `min(:Event.number)` … `max(:Event.number)` split into **three as-equal-as-possible** buckets. Not fixed to “scene 21 / 65”; changes with whatever script is loaded.

## Key metrics (current UI)

- **Momentum heat (per scene):** `CONFLICTS_WITH / (INTERACTS_WITH + CONFLICTS_WITH)` among entities both `IN_SCENE` to that `Event`; UI smooths with a **3-scene** trailing mean.
- **Payoff props:** First intro (earliest `IN_SCENE` or co-scene `POSSESSES`) vs last `USES` / `CONFLICTS_WITH`; keep if gap **> 10** scenes.
- **Passivity (per act window):** `in / (in + out)` on `CONFLICTS_WITH` + `USES` (incl. incoming `USES` on possessed props), edges attributed to scenes in the act range. **Power shift** uses top **5** characters by **CONFLICTS_WITH + USES + INTERACTS_WITH** count (both directions).
- **Protagonist check:** If **`zev`** (see `PROTAGONIST_ID` in `app.py`) has **Act 3 passivity > Act 1**, UI shows a regression warning.

## Separate: “scene heat” in `metrics.py`

**Distinct** from momentum heat: **unique unordered conflict pairs** in-scene ÷ `IN_SCENE` count (`get_scene_heat`). Still used in CLI / diagnostics; not the same formula as the momentum chart.

## Pipeline order (cold start)

`parser.py` → `lexicon.py` → `ingest.py` → `neo4j_loader.py` → `streamlit run app.py`

## Secrets

**`.env`** only; never commit. Template: **`.env.example`**.
