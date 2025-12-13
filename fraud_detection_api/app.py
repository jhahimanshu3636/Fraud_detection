# app.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os

from fraud_engine import FraudDetectionEngine

app = FastAPI(title="Fraud Detection API")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


class CompanyResponse(BaseModel):
    riskscore: float
    opportunityscore: float
    patterns: Dict[str, Any]
    visualizationdata: Dict[str, Any]


def build_visualization_data(
    company_id: str,
    engine: FraudDetectionEngine,
) -> Dict[str, Any]:
    """
    2-hop neighborhood visualization data for the given company.
    Mirrors your existing logic but reuses engine's Neo4j driver.
    """
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    node_index: Dict[str, int] = {}

    with engine.driver.session() as session:
        query = """
        MATCH (center:Company {company_id: $company_id})
        MATCH (center)-[r1*1..2]-(neighbor)
        WHERE NOT neighbor:Invoice
        WITH DISTINCT center, neighbor
        OPTIONAL MATCH (center)-[r:SUPPLIES|SUBSIDIARY_OF|OWNS_SHARE|AUDITED_BY]-(neighbor)
        WITH DISTINCT
            coalesce(neighbor.company_id, neighbor.shareholder_id, neighbor.auditor_id) AS id,
            neighbor,
            r,
            labels(neighbor)[0] AS type,
            coalesce(neighbor.risk_score, 0.0) AS riskScore
        RETURN DISTINCT
            id,
            type,
            riskScore,
            coalesce(neighbor.name, id) AS label,
            type(r) AS relationshipType,
            coalesce(r.percentage, r.annual_volume, 1.0) AS weight
        ORDER BY riskScore DESC
        """
        result = session.run(query, company_id=company_id)

        # Add center node
        center_node = {
            "id": company_id,
            "label": f"Company {company_id}",
            "riskscore": 0.0,
            "type": "Company",
            "size": 25,
        }
        nodes.append(center_node)
        node_index[company_id] = 0

        for record in result:
            node_id = record["id"]
            if node_id is None:
                continue
            if node_id not in node_index:
                risk = float(record["riskScore"])
                size = max(10.0, 25.0 - risk * 15.0)
                color = "red" if risk >= 0.7 else "orange" if risk >= 0.4 else "green"
                node_index[node_id] = len(nodes)
                nodes.append(
                    {
                        "id": node_id,
                        "label": record["label"],
                        "riskscore": risk,
                        "type": record["type"],
                        "size": size,
                        "color": color,
                    }
                )

            rel_type = record["relationshipType"]
            weight = float(record["weight"])
            edges.append(
                {
                    "from": node_index[company_id],
                    "to": node_index[node_id],
                    "label": rel_type,
                    "width": weight / 10.0 if weight else 1.0,
                }
            )

    return {"nodes": nodes, "edges": edges}


@app.get("/company/{company_id}", response_model=CompanyResponse)
async def get_company_analysis(company_id: str) -> CompanyResponse:
    """
    For the input company_id, compute pattern scores and return:
    - risk score
    - opportunity score
    - patterns for all three patterns
    - 2-hop visualization data
    """
    engine = FraudDetectionEngine(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        risk, opportunity, patterns = engine.analyze_company(company_id)

        # If the company truly doesn't exist, you may want to check here
        # by attempting to load it from Neo4j; omitted for brevity.

        viz_data = build_visualization_data(company_id, engine)

        return CompanyResponse(
            riskscore=float(risk),
            opportunityscore=float(opportunity),
            patterns=patterns,
            visualizationdata=viz_data,
        )
    finally:
        engine.close()


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "healthy"}