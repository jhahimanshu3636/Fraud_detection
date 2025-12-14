# # app.py

# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import List, Dict, Any
# import os

# from fraud_engine import FraudDetectionEngine

# app = FastAPI(title="Fraud Detection API")

# # Add CORS middleware to allow requests from the web interface
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all origins (for local file:// access)
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
# )

# NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
# NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
# NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


# class CompanyResponse(BaseModel):
#     riskscore: float
#     opportunityscore: float
#     patterns: Dict[str, Any]
#     visualizationdata: Dict[str, Any]


# def build_visualization_data(
#     company_id: str,
#     engine: FraudDetectionEngine,
# ) -> Dict[str, Any]:
#     """
#     2-hop neighborhood visualization - ONLY connected nodes with actual relationship paths.
#     """
#     nodes: List[Dict[str, Any]] = []
#     edges: List[Dict[str, Any]] = []
#     node_index: Dict[str, int] = {}

#     with engine.driver.session() as session:
#         # Check if company exists
#         check_query = """
#         MATCH (c:Company) 
#         WHERE toLower(c.company_id) = toLower($company_id)
#         RETURN c.company_id as id, c.name as name, coalesce(c.risk_score, 0.0) as risk_score
#         """
#         check_result = session.run(check_query, company_id=company_id)
#         company_record = check_result.single()
        
#         if not company_record:
#             return {"nodes": [], "edges": []}
        
#         actual_company_id = company_record['id']
        
#         # Add center node
#         center_node = {
#             'id': actual_company_id,
#             'label': actual_company_id,
#             'riskscore': float(company_record['risk_score']),
#             'type': 'Company',
#             'size': 30,
#             'color': '#3b82f6'
#         }
#         nodes.append(center_node)
#         node_index[actual_company_id] = 0
        
#         # Get connected nodes (paths up to 2 hops with specific relationship types)
#         query = """
#         MATCH path = (center:Company {company_id: $company_id})-[*1..2]-(neighbor)
#         WHERE NOT neighbor:Invoice 
#           AND neighbor <> center
#           AND ALL(r IN relationships(path) 
#               WHERE type(r) IN ['SUPPLIES', 'SUBSIDIARY_OF', 'OWNS_SHARE', 'AUDITED_BY'])
        
#         WITH DISTINCT neighbor
        
#         RETURN 
#             coalesce(neighbor.company_id, neighbor.shareholder_id, neighbor.auditor_id) AS id,
#             labels(neighbor)[0] AS type,
#             coalesce(neighbor.risk_score, 0.0) AS riskScore
#         """
#         result = session.run(query, company_id=actual_company_id)

#         connected_nodes = set([actual_company_id])
        
#         for record in result:
#             node_id = record["id"]
#             if node_id and node_id != actual_company_id and node_id not in node_index:
#                 connected_nodes.add(node_id)
#                 risk = float(record["riskScore"])
#                 size = max(12.0, 28.0 - risk * 16.0)
                
#                 if risk >= 0.7:
#                     color = "#ef4444"
#                 elif risk >= 0.4:
#                     color = "#f59e0b"
#                 else:
#                     color = "#10b981"
                
#                 node_index[node_id] = len(nodes)
#                 nodes.append({
#                     "id": node_id,
#                     "label": node_id,
#                     "riskscore": risk,
#                     "type": record["type"],
#                     "size": size,
#                     "color": color,
#                 })
        
#         # Get edges between connected nodes
#         edge_query = """
#         MATCH (n1)-[r:SUPPLIES|SUBSIDIARY_OF|OWNS_SHARE|AUDITED_BY]-(n2)
#         WHERE NOT n1:Invoice AND NOT n2:Invoice
#           AND coalesce(n1.company_id, n1.shareholder_id, n1.auditor_id) IN $node_ids
#           AND coalesce(n2.company_id, n2.shareholder_id, n2.auditor_id) IN $node_ids
        
#         RETURN DISTINCT
#             coalesce(n1.company_id, n1.shareholder_id, n1.auditor_id) as fromId,
#             coalesce(n2.company_id, n2.shareholder_id, n2.auditor_id) as toId,
#             type(r) as relType,
#             coalesce(r.percentage, r.annual_volume, 1.0) as weight
#         """
        
#         edge_result = session.run(edge_query, node_ids=list(connected_nodes))
        
#         added_edges = set()
#         for record in edge_result:
#             from_id = record["fromId"]
#             to_id = record["toId"]
            
#             if from_id in node_index and to_id in node_index:
#                 edge_key = tuple(sorted([from_id, to_id]))
#                 if edge_key not in added_edges:
#                     added_edges.add(edge_key)
#                     edges.append({
#                         "from": node_index[from_id],
#                         "to": node_index[to_id],
#                         "label": record["relType"],
#                         "width": max(1.0, float(record["weight"]) / 10.0),
#                     })

#     return {"nodes": nodes, "edges": edges}


# @app.get("/company/{company_id}", response_model=CompanyResponse)
# async def get_company_analysis(company_id: str) -> CompanyResponse:
#     """
#     For the input company_id, compute pattern scores and return:
#     - risk score
#     - opportunity score
#     - patterns for all three patterns
#     - 2-hop visualization data
#     """
#     engine = FraudDetectionEngine(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
#     try:
#         # Check if company exists (case-insensitive)
#         with engine.driver.session() as session:
#             result = session.run(
#                 "MATCH (c:Company) WHERE toLower(c.company_id) = toLower($company_id) RETURN c.company_id as actual_id",
#                 company_id=company_id
#             )
#             record = result.single()
#             if not record:
#                 raise HTTPException(
#                     status_code=404,
#                     detail=f"Company '{company_id}' not found in database"
#                 )
#             # Use the actual company_id from database (preserves case)
#             actual_company_id = record['actual_id']
        
#         # Analyze company with actual ID from database
#         risk, opportunity, patterns = engine.analyze_company(actual_company_id)
#         viz_data = build_visualization_data(actual_company_id, engine)
        
#         # Check if we have any nodes (at least the center node)
#         if not viz_data['nodes'] or len(viz_data['nodes']) == 0:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"No network data found for company '{actual_company_id}'"
#             )

#         return CompanyResponse(
#             riskscore=float(risk),
#             opportunityscore=float(opportunity),
#             patterns=patterns,
#             visualizationdata=viz_data,
#         )
#     finally:
#         engine.close()


# @app.get("/health")
# async def health() -> Dict[str, str]:
#     return {"status": "healthy"}


# @app.get("/company/{company_id}/visualize")
# async def visualize_company_network(company_id: str):
#     """
#     Generate and return an interactive HTML visualization for the company network.
#     """
#     from fastapi.responses import HTMLResponse
#     from visualization import create_visualization_for_company
#     import os
    
#     try:
#         # Generate visualization
#         output_path = f'/tmp/fraud_network_{company_id}.html'
#         html_file = create_visualization_for_company(
#             company_id=company_id,
#             neo4j_uri=NEO4J_URI,
#             neo4j_user=NEO4J_USER,
#             neo4j_password=NEO4J_PASSWORD,
#             output_path=output_path
#         )
        
#         # Read and return HTML
#         with open(html_file, 'r', encoding='utf-8') as f:
#             html_content = f.read()
        
#         # Clean up temp file
#         if os.path.exists(html_file):
#             os.remove(html_file)
        
#         return HTMLResponse(content=html_content)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Visualization failed: {str(e)}")



# app.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os

from fraud_engine import FraudDetectionEngine

app = FastAPI(title="Fraud Detection API")

# Add CORS middleware to allow requests from the web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for local file:// access)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

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
    2-hop neighborhood visualization with DIRECTIONAL edges for circular patterns.
    """
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    node_index: Dict[str, int] = {}

    with engine.driver.session() as session:
        # Check if company exists
        check_query = """
        MATCH (c:Company) 
        WHERE toLower(c.company_id) = toLower($company_id)
        RETURN c.company_id as id, c.name as name, coalesce(c.risk_score, 0.0) as risk_score
        """
        check_result = session.run(check_query, company_id=company_id)
        company_record = check_result.single()
        
        if not company_record:
            return {"nodes": [], "edges": []}
        
        actual_company_id = company_record['id']
        
        # Add center node
        center_node = {
            'id': actual_company_id,
            'label': actual_company_id,
            'riskscore': float(company_record['risk_score']),
            'type': 'Company',
            'size': 30,
            'color': '#3b82f6'
        }
        nodes.append(center_node)
        node_index[actual_company_id] = 0
        
        # Get connected nodes (paths up to 2 hops)
        query = """
        MATCH path = (center:Company {company_id: $company_id})-[*1..2]-(neighbor)
        WHERE NOT neighbor:Invoice 
          AND neighbor <> center
          AND ALL(r IN relationships(path) 
              WHERE type(r) IN ['SUPPLIES', 'SUBSIDIARY_OF', 'OWNS_SHARE', 'AUDITED_BY'])
        
        WITH DISTINCT neighbor
        
        RETURN 
            coalesce(neighbor.company_id, neighbor.shareholder_id, neighbor.auditor_id) AS id,
            labels(neighbor)[0] AS type,
            coalesce(neighbor.risk_score, 0.0) AS riskScore
        """
        result = session.run(query, company_id=actual_company_id)

        connected_nodes = set([actual_company_id])
        
        for record in result:
            node_id = record["id"]
            if node_id and node_id != actual_company_id and node_id not in node_index:
                connected_nodes.add(node_id)
                risk = float(record["riskScore"])
                size = max(12.0, 28.0 - risk * 16.0)
                
                if risk >= 0.7:
                    color = "#ef4444"
                elif risk >= 0.4:
                    color = "#f59e0b"
                else:
                    color = "#10b981"
                
                node_index[node_id] = len(nodes)
                nodes.append({
                    "id": node_id,
                    "label": node_id,
                    "riskscore": risk,
                    "type": record["type"],
                    "size": size,
                    "color": color,
                })
        
        # CRITICAL FIX: Get DIRECTIONAL edges between all connected nodes
        # This is essential for showing circular trade patterns correctly
        edge_query = """
        MATCH (n1)-[r:SUPPLIES|SUBSIDIARY_OF|OWNS_SHARE|AUDITED_BY]->(n2)
        WHERE NOT n1:Invoice AND NOT n2:Invoice
          AND coalesce(n1.company_id, n1.shareholder_id, n1.auditor_id) IN $node_ids
          AND coalesce(n2.company_id, n2.shareholder_id, n2.auditor_id) IN $node_ids
        
        RETURN DISTINCT
            coalesce(n1.company_id, n1.shareholder_id, n1.auditor_id) as fromId,
            coalesce(n2.company_id, n2.shareholder_id, n2.auditor_id) as toId,
            type(r) as relType,
            coalesce(r.percentage, r.annual_volume, 1.0) as weight
        """
        
        edge_result = session.run(edge_query, node_ids=list(connected_nodes))
        
        # Keep all directed edges - DO NOT deduplicate to preserve cycles
        for record in edge_result:
            from_id = record["fromId"]
            to_id = record["toId"]
            
            if from_id in node_index and to_id in node_index:
                edges.append({
                    "from": node_index[from_id],
                    "to": node_index[to_id],
                    "label": record["relType"],
                    "width": max(1.0, float(record["weight"]) / 10.0),
                })

    return {"nodes": nodes, "edges": edges}


@app.get("/company/{company_id}", response_model=CompanyResponse)
async def get_company_analysis(company_id: str) -> CompanyResponse:
    """
    For the input company_id, compute pattern scores and return:
    - risk score
    - opportunity score
    - patterns for all three patterns
    - 2-hop visualization data with directional edges
    """
    engine = FraudDetectionEngine(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        # Check if company exists (case-insensitive)
        with engine.driver.session() as session:
            result = session.run(
                "MATCH (c:Company) WHERE toLower(c.company_id) = toLower($company_id) RETURN c.company_id as actual_id",
                company_id=company_id
            )
            record = result.single()
            if not record:
                raise HTTPException(
                    status_code=404,
                    detail=f"Company '{company_id}' not found in database"
                )
            # Use the actual company_id from database (preserves case)
            actual_company_id = record['actual_id']
        
        # Analyze company with actual ID from database
        risk, opportunity, patterns = engine.analyze_company(actual_company_id)
        viz_data = build_visualization_data(actual_company_id, engine)
        
        # Check if we have any nodes (at least the center node)
        if not viz_data['nodes'] or len(viz_data['nodes']) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No network data found for company '{actual_company_id}'"
            )

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


@app.get("/company/{company_id}/visualize")
async def visualize_company_network(company_id: str):
    """
    Generate and return an interactive HTML visualization for the company network.
    """
    from fastapi.responses import HTMLResponse
    from visualization import create_visualization_for_company
    import os
    
    try:
        # Generate visualization
        output_path = f'/tmp/fraud_network_{company_id}.html'
        html_file = create_visualization_for_company(
            company_id=company_id,
            neo4j_uri=NEO4J_URI,
            neo4j_user=NEO4J_USER,
            neo4j_password=NEO4J_PASSWORD,
            output_path=output_path
        )
        
        # Read and return HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Clean up temp file
        if os.path.exists(html_file):
            os.remove(html_file)
        
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization failed: {str(e)}")