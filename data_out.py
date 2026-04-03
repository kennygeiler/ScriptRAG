"""Export and demo-query helpers for manipulable graph data (Neo4j).

All Cypher uses parameters — no string interpolation from callers.
"""

from __future__ import annotations

from typing import Any, TypedDict

from neo4j import Session

from metrics import NARRATIVE_REL_TYPES

__all__ = [
    "DEMO_QUERY_SPECS",
    "graph_schema_card_markdown",
    "get_label_counts",
    "get_rel_type_counts",
    "run_demo_query",
    "rows_narrative_edges",
    "rows_characters",
    "rows_events",
]


def graph_schema_card_markdown() -> str:
    return """### Graph model (ScriptRAG)

**Node labels:** `Character`, `Location`, `Prop`, `Event`

**Structural relationship:** `IN_SCENE` — entity present in a scene (`Event`).

**Narrative relationships** (typed; carry `source_quote` on the relationship where applicable):
`INTERACTS_WITH`, `CONFLICTS_WITH`, `USES`, `LOCATED_IN`, `POSSESSES`

**Downstream use:** Query in Neo4j/Bolt, export edge/entity tables below, or point BI tools at a JDBC/Arrow bridge. Checkpoint JSON on disk: `validated_graph.json`.
"""


def get_label_counts(session: Session) -> list[dict[str, Any]]:
    return session.run(
        """
        MATCH (n)
        UNWIND labels(n) AS lab
        RETURN lab AS label, count(*) AS cnt
        ORDER BY cnt DESC
        """
    ).data()


def get_rel_type_counts(session: Session) -> list[dict[str, Any]]:
    return session.run(
        """
        MATCH ()-[r]->()
        RETURN type(r) AS rel_type, count(*) AS cnt
        ORDER BY cnt DESC
        """
    ).data()


def rows_narrative_edges(session: Session, *, limit: int) -> list[dict[str, Any]]:
    types = list(NARRATIVE_REL_TYPES)
    return session.run(
        """
        MATCH (a)-[r]->(b)
        WHERE type(r) IN $types
        RETURN labels(a)[0] AS source_label,
               a.id AS source_id,
               type(r) AS rel_type,
               labels(b)[0] AS target_label,
               b.id AS target_id,
               r.source_quote AS source_quote
        ORDER BY source_id, rel_type, target_id
        LIMIT $limit
        """,
        types=types,
        limit=int(limit),
    ).data()


def rows_characters(session: Session) -> list[dict[str, Any]]:
    return session.run(
        """
        MATCH (c:Character)
        RETURN c.id AS id, c.name AS name
        ORDER BY toLower(c.name), c.id
        """
    ).data()


def rows_events(session: Session) -> list[dict[str, Any]]:
    return session.run(
        """
        MATCH (e:Event)
        RETURN e.number AS number, e.heading AS heading
        ORDER BY e.number
        """
    ).data()


class DemoQuerySpec(TypedDict):
    key: str
    title: str
    description: str


# Queries are fixed strings; parameters only where $types is required.
DEMO_QUERY_SPECS: tuple[DemoQuerySpec, ...] = (
    {
        "key": "scene_count",
        "title": "Scene (Event) count",
        "description": "How many :Event nodes — one per screenplay scene heading.",
    },
    {
        "key": "narrative_counts",
        "title": "Narrative edges by type",
        "description": "Counts for INTERACTS_WITH, CONFLICTS_WITH, USES, LOCATED_IN, POSSESSES.",
    },
    {
        "key": "top_conflict_chars",
        "title": "Top characters by CONFLICTS_WITH (out + in)",
        "description": "Structural friction signal — degree on conflict edges.",
    },
    {
        "key": "sample_quotes",
        "title": "Sample narrative edges with source_quote",
        "description": "Up to 50 edges showing proof text attached to relationships.",
    },
)


def run_demo_query(session: Session, key: str) -> list[dict[str, Any]]:
    types = list(NARRATIVE_REL_TYPES)
    if key == "scene_count":
        return session.run(
            "MATCH (e:Event) RETURN count(e) AS scene_count"
        ).data()
    if key == "narrative_counts":
        return session.run(
            """
            MATCH ()-[r]->()
            WHERE type(r) IN $types
            RETURN type(r) AS rel_type, count(*) AS cnt
            ORDER BY cnt DESC
            """,
            types=types,
        ).data()
    if key == "top_conflict_chars":
        return session.run(
            """
            MATCH (c:Character)
            OPTIONAL MATCH (c)-[o:CONFLICTS_WITH]->()
            OPTIONAL MATCH ()-[i:CONFLICTS_WITH]->(c)
            WITH c, count(DISTINCT o) AS out_c, count(DISTINCT i) AS in_c
            RETURN c.id AS id, c.name AS name, out_c + in_c AS conflict_degree
            ORDER BY conflict_degree DESC, toLower(c.name)
            LIMIT 25
            """
        ).data()
    if key == "sample_quotes":
        return session.run(
            """
            MATCH (a)-[r]->(b)
            WHERE type(r) IN $types AND r.source_quote IS NOT NULL AND r.source_quote <> ''
            RETURN labels(a)[0] AS src_label, a.id AS source_id,
                   type(r) AS rel_type,
                   labels(b)[0] AS tgt_label, b.id AS target_id,
                   r.source_quote AS source_quote
            LIMIT 50
            """,
            types=types,
        ).data()
    raise ValueError(f"unknown demo query key: {key!r}")
