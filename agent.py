from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph

load_dotenv()

_log = logging.getLogger(__name__)

# Hard-locked Cypher prompt; template uses only {question} (LangChain-injected graph schema is not referenced here).
CYPHER_GENERATION_TEMPLATE = """Task: Generate a Cypher query to answer the user question.

Graph schema (strict):
- Node labels ONLY: :Character, :Location, :Prop, :Event. Never use :Entity or other labels.
- Structural: (n)-[:IN_SCENE]->(e:Event) where n is :Character, :Location, or :Prop — means n appears in that scene.
- Narrative edges between entities use types INTERACTS_WITH, LOCATED_IN, USES, CONFLICTS_WITH, POSSESSES and store proof text on r.source_quote (never justification).

The Dictionary:

Who is in a scene? Use (c:Character)-[:IN_SCENE]->(e:Event) (and similarly Location/Prop with IN_SCENE).

The 'Walk' Command (locations): When the user asks about a location, setting, or where something happens, the Cypher MUST use:
OPTIONAL MATCH (e:Event)-[:LOCATED_IN]-(l:Location)
Combine this with your main MATCH patterns so connected Location nodes are always traversed. Do not answer location questions without walking this relationship.

Location Data Priority: If l.name exists, return it as the primary Location. Only if l.name is null should you fallback to the e.name string (use COALESCE(l.name, e.name) or equivalent in RETURN).

Property Validation: When the question involves characters and locations together, ensure the final RETURN includes l.name and c.name (e.g. RETURN c.name, l.name, e.number as needed).

Where is the scene? Use (e:Event)-[:LOCATED_IN]-(l:Location) in addition to the OPTIONAL MATCH walk above when resolving locations.

What items are there? Character/Prop USES edges are (a)-[:USES]->(b); co-presence in a scene is often via shared IN_SCENE to the same Event.

What is the conflict? Use (c:Character)-[:CONFLICTS_WITH]-(other:Character).

No More Excuses (Cypher): Never design a query whose natural-language interpretation would claim "specific location details are not provided" if a :LOCATED_IN path to :Location exists in the graph — follow the relationship and return l.name.

The Formatting Rules:

Labels: ALWAYS :Character, :Location, :Prop, :Event.

Property: Use e.number for Event sequencing. Use n.name for display.

Fuzzy Search: Use toLower(n.name) CONTAINS toLower('user_input').

The 'Strict' Clause: Allowed relationship types ONLY: IN_SCENE, INTERACTS_WITH, LOCATED_IN, USES, POSSESSES, CONFLICTS_WITH. Do not use APPEARS_IN, PART_OF, AT_LOCATION, DISCUSSES, FORESHADOWS, CAUSES, or any other type.

Return: Always RETURN the names and numbers clearly so the response isn't empty.

Question: {question}
Cypher Query:"""

cypher_prompt = PromptTemplate(template=CYPHER_GENERATION_TEMPLATE, input_variables=["question"])

QA_ANSWER_TEMPLATE = """You are an assistant that forms human-readable answers from graph query results.
The provided information is authoritative — use it directly. If you see a relationship or field in the context, follow it; do not invent gaps.
Never output the phrase "specific location details are not provided" when the context includes Location data, l.name, or any connected location fields — state the names from the data.
If l.name exists in the context, treat it as the primary location name; only if there is no location name should you refer to the Event name as fallback.

If the provided information is empty, say that you don't know the answer.

Information:
{context}

Question: {question}
Helpful Answer:"""

qa_prompt = PromptTemplate(template=QA_ANSWER_TEMPLATE, input_variables=["context", "question"])

_graph: Neo4jGraph | None = None
_chain: GraphCypherQAChain | None = None
_chain_init_failed = False

# If the Neo4j server has the APOC plugin, set refresh_schema=True for full schema introspection.
llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)


def _get_chain() -> GraphCypherQAChain | None:
    global _graph, _chain, _chain_init_failed
    if _chain is not None:
        return _chain
    if _chain_init_failed:
        return None
    uri = os.environ.get("NEO4J_URI", "").strip()
    user = os.environ.get("NEO4J_USER", "").strip()
    password = os.environ.get("NEO4J_PASSWORD", "").strip()
    if not uri or not user or not password:
        _log.warning(
            "Investigate: missing NEO4J_URI, NEO4J_USER, or NEO4J_PASSWORD — chain disabled"
        )
        _chain_init_failed = True
        return None
    try:
        _graph = Neo4jGraph(
            url=uri,
            username=user,
            password=password,
            refresh_schema=False,
        )
        _chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=_graph,
            cypher_prompt=cypher_prompt,
            qa_prompt=qa_prompt,
            verbose=True,
            allow_dangerous_requests=True,
        )
        return _chain
    except Exception:
        _log.exception("Investigate: Neo4j graph or chain init failed")
        _chain_init_failed = True
        return None


def ask_narrative_mri(query: str) -> str:
    c = _get_chain()
    if c is None:
        return (
            "The investigation assistant could not connect to Neo4j. Check NEO4J_URI, "
            "NEO4J_USER, NEO4J_PASSWORD in .env and that the database is reachable."
        )
    try:
        result = c.invoke({"query": query})
        out = result.get("result", result)
        return out if isinstance(out, str) else str(out)
    except Exception:
        _log.exception("Investigate: chain.invoke failed")
        return "Query failed — check Neo4j and server logs."


if __name__ == "__main__":
    print("Checking connection to Neo4j...")
    print(ask_narrative_mri("How many Character nodes are in the database?"))
