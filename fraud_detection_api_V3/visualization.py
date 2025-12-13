"""
Network Visualization Module for Fraud Detection
Uses NetworkX for graph structure and generates interactive D3.js visualization
"""

import json
import networkx as nx
from typing import Dict, List, Any, Optional
from fraud_engine import FraudDetectionEngine


class FraudNetworkVisualizer:
    """Generate interactive network visualizations for fraud detection patterns."""
    
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.engine = FraudDetectionEngine(neo4j_uri, neo4j_user, neo4j_password)
        self.graph = nx.Graph()
    
    def close(self):
        self.engine.close()
    
    def build_network_graph(self, company_id: str) -> Dict[str, Any]:
        """
        Build a 2-hop network graph for the given company with pattern highlighting.
        
        Returns:
            Dictionary with nodes, edges, and pattern information
        """
        # Get analysis results
        risk_score, opportunity_score, patterns = self.engine.analyze_company(company_id)
        
        # Get 2-hop neighborhood
        viz_data = self._get_2hop_neighborhood(company_id)
        
        # Build NetworkX graph
        self.graph.clear()
        
        # Add nodes with attributes
        for node in viz_data['nodes']:
            self.graph.add_node(
                node['id'],
                label=node['label'],
                node_type=node['type'],
                risk_score=node.get('riskscore', 0.0),
                size=node.get('size', 15),
                color=node.get('color', 'gray')
            )
        
        # Add edges with attributes
        for edge in viz_data['edges']:
            from_id = viz_data['nodes'][edge['from']]['id']
            to_id = viz_data['nodes'][edge['to']]['id']
            self.graph.add_edge(
                from_id,
                to_id,
                label=edge['label'],
                width=edge.get('width', 1.0)
            )
        
        # Highlight patterns
        pattern_highlights = self._identify_pattern_highlights(
            company_id, patterns, viz_data
        )
        
        return {
            'nodes': viz_data['nodes'],
            'edges': viz_data['edges'],
            'patterns': {
                'shell_chains': patterns['pattern1_shell'],
                'circular_trade': patterns['pattern2_circular'],
                'hidden_influence': patterns['pattern3_hidden']
            },
            'highlights': pattern_highlights,
            'risk_score': risk_score,
            'opportunity_score': opportunity_score,
            'stats': {
                'total_nodes': len(viz_data['nodes']),
                'total_edges': len(viz_data['edges']),
                'high_risk_nodes': sum(1 for n in viz_data['nodes'] if n.get('riskscore', 0) >= 0.7)
            }
        }
    
    def _get_2hop_neighborhood(self, company_id: str) -> Dict[str, Any]:
        """Get 2-hop neighborhood from Neo4j."""
        nodes = []
        edges = []
        node_index = {}
        
        with self.engine.driver.session() as session:
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
                'id': company_id,
                'label': f'Company {company_id}',
                'riskscore': 0.0,
                'type': 'Company',
                'size': 30,
                'color': '#4A90E2'  # Blue for center
            }
            nodes.append(center_node)
            node_index[company_id] = 0
            
            # Add neighboring nodes
            for record in result:
                node_id = record['id']
                if node_id is None or node_id == company_id:
                    continue
                
                if node_id not in node_index:
                    risk = float(record['riskScore'])
                    size = max(10.0, 25.0 - risk * 15.0)
                    
                    # Color coding based on risk
                    if risk >= 0.7:
                        color = '#E74C3C'  # Red for high risk
                    elif risk >= 0.4:
                        color = '#F39C12'  # Orange for medium risk
                    else:
                        color = '#27AE60'  # Green for low risk
                    
                    node_index[node_id] = len(nodes)
                    nodes.append({
                        'id': node_id,
                        'label': record['label'],
                        'riskscore': risk,
                        'type': record['type'],
                        'size': size,
                        'color': color
                    })
                
                # Add edge
                rel_type = record['relationshipType']
                if rel_type:
                    weight = float(record['weight'])
                    edges.append({
                        'from': node_index[company_id],
                        'to': node_index[node_id],
                        'label': rel_type,
                        'width': max(1.0, weight / 10.0) if weight else 1.0
                    })
        
        return {'nodes': nodes, 'edges': edges}
    
    def _identify_pattern_highlights(
        self, 
        company_id: str, 
        patterns: Dict[str, Any],
        viz_data: Dict[str, Any]
    ) -> Dict[str, List[Any]]:
        """Identify nodes and edges to highlight for each pattern."""
        highlights = {
            'shell_chains': [],
            'circular_cycles': [],
            'hidden_influence': []
        }
        
        # Extract node IDs for easy lookup
        node_ids = {node['id']: idx for idx, node in enumerate(viz_data['nodes'])}
        
        # Pattern 1: Shell Company Chains
        for shell_pattern in patterns['pattern1_shell']:
            chain = shell_pattern['chain']
            if company_id in chain:
                chain_indices = [node_ids[c] for c in chain if c in node_ids]
                highlights['shell_chains'].append({
                    'nodes': chain_indices,
                    'auditor': shell_pattern['auditorId'],
                    'risk_score': shell_pattern['riskScore']
                })
        
        # Pattern 2: Circular Trade
        for cycle_pattern in patterns['pattern2_circular']:
            cycle = cycle_pattern['cycle']
            if company_id in cycle:
                cycle_indices = [node_ids[c] for c in cycle if c in node_ids]
                highlights['circular_cycles'].append({
                    'nodes': cycle_indices,
                    'total_volume': cycle_pattern['totalVolume'],
                    'isolation_score': cycle_pattern['isolationScore']
                })
        
        # Pattern 3: Hidden Influence
        for hidden_pattern in patterns['pattern3_hidden']:
            involved_ids = [
                hidden_pattern['shareholderId'],
                hidden_pattern['supplierId'],
                company_id
            ]
            involved_indices = [node_ids[i] for i in involved_ids if i in node_ids]
            highlights['hidden_influence'].append({
                'nodes': involved_indices,
                'shareholder': hidden_pattern['shareholderId'],
                'supplier': hidden_pattern['supplierId'],
                'concentration': hidden_pattern['concentrationPct']
            })
        
        return highlights
    
    def generate_html_visualization(
        self, 
        company_id: str, 
        output_path: str = 'fraud_network_viz.html'
    ) -> str:
        """
        Generate an interactive HTML visualization using D3.js/vis.js.
        
        Args:
            company_id: Company ID to visualize
            output_path: Path to save the HTML file
            
        Returns:
            Path to the generated HTML file
        """
        # Build network graph
        network_data = self.build_network_graph(company_id)
        
        # Generate HTML with embedded JavaScript
        html_content = self._generate_html_template(company_id, network_data)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _generate_html_template(self, company_id: str, network_data: Dict[str, Any]) -> str:
        """Generate HTML template with D3.js visualization."""
        
        # Convert data to JSON
        nodes_json = json.dumps(network_data['nodes'], indent=2)
        edges_json = json.dumps(network_data['edges'], indent=2)
        highlights_json = json.dumps(network_data['highlights'], indent=2)
        patterns_json = json.dumps(network_data['patterns'], indent=2)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fraud Detection Network - Company {company_id}</title>
    <script src="https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header .company-id {{
            font-size: 1.2em;
            opacity: 0.9;
            font-weight: 300;
        }}
        
        .stats-bar {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-card .label {{
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-card.risk {{
            border-left: 4px solid #E74C3C;
        }}
        
        .stat-card.opportunity {{
            border-left: 4px solid #27AE60;
        }}
        
        .stat-card.info {{
            border-left: 4px solid #4A90E2;
        }}
        
        .main-content {{
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 20px;
            padding: 20px;
        }}
        
        #network-container {{
            height: 700px;
            border: 2px solid #dee2e6;
            border-radius: 12px;
            background: #fafafa;
            position: relative;
        }}
        
        .controls {{
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 1000;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        
        .controls button {{
            display: block;
            width: 100%;
            padding: 10px 15px;
            margin: 5px 0;
            border: none;
            border-radius: 6px;
            background: #4A90E2;
            color: white;
            cursor: pointer;
            font-size: 0.9em;
            transition: background 0.2s;
        }}
        
        .controls button:hover {{
            background: #357ABD;
        }}
        
        .controls button.active {{
            background: #27AE60;
        }}
        
        .sidebar {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            overflow-y: auto;
            max-height: 700px;
        }}
        
        .pattern-section {{
            margin-bottom: 25px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #4A90E2;
        }}
        
        .pattern-section h3 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .pattern-item {{
            background: #f8f9fa;
            padding: 10px;
            margin: 8px 0;
            border-radius: 6px;
            font-size: 0.9em;
        }}
        
        .pattern-item strong {{
            color: #495057;
        }}
        
        .legend {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .legend h3 {{
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
        }}
        
        .no-patterns {{
            text-align: center;
            color: #6c757d;
            padding: 20px;
            font-style: italic;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 8px;
        }}
        
        .badge.high-risk {{
            background: #E74C3C;
            color: white;
        }}
        
        .badge.medium-risk {{
            background: #F39C12;
            color: white;
        }}
        
        .badge.low-risk {{
            background: #27AE60;
            color: white;
        }}
        
        @media (max-width: 1200px) {{
            .main-content {{
                grid-template-columns: 1fr;
            }}
            
            .sidebar {{
                max-height: 500px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Fraud Detection Network Visualization</h1>
            <div class="company-id">Company: {company_id}</div>
        </div>
        
        <div class="stats-bar">
            <div class="stat-card risk">
                <div class="value">{network_data['risk_score']:.2f}</div>
                <div class="label">Risk Score</div>
            </div>
            <div class="stat-card opportunity">
                <div class="value">{network_data['opportunity_score']:.2f}</div>
                <div class="label">Opportunity Score</div>
            </div>
            <div class="stat-card info">
                <div class="value">{network_data['stats']['total_nodes']}</div>
                <div class="label">Total Entities</div>
            </div>
            <div class="stat-card info">
                <div class="value">{network_data['stats']['total_edges']}</div>
                <div class="label">Relationships</div>
            </div>
            <div class="stat-card risk">
                <div class="value">{network_data['stats']['high_risk_nodes']}</div>
                <div class="label">High Risk Nodes</div>
            </div>
        </div>
        
        <div class="main-content">
            <div>
                <div id="network-container">
                    <div class="controls">
                        <button id="highlight-shell" onclick="highlightPattern('shell')">
                            🔗 Shell Chains
                        </button>
                        <button id="highlight-circular" onclick="highlightPattern('circular')">
                            🔄 Circular Trade
                        </button>
                        <button id="highlight-hidden" onclick="highlightPattern('hidden')">
                            👁️ Hidden Influence
                        </button>
                        <button id="reset-view" onclick="resetView()">
                            ↺ Reset View
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="legend">
                    <h3>Legend</h3>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #E74C3C;"></div>
                        <span>High Risk (≥0.7)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #F39C12;"></div>
                        <span>Medium Risk (0.4-0.7)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #27AE60;"></div>
                        <span>Low Risk (<0.4)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #4A90E2;"></div>
                        <span>Query Company</span>
                    </div>
                </div>
                
                <div class="pattern-section">
                    <h3>🔗 Shell Company Chains</h3>
                    <div id="shell-patterns"></div>
                </div>
                
                <div class="pattern-section">
                    <h3>🔄 Circular Trade Patterns</h3>
                    <div id="circular-patterns"></div>
                </div>
                
                <div class="pattern-section">
                    <h3>👁️ Hidden Influence Patterns</h3>
                    <div id="hidden-patterns"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Network data
        const nodesData = {nodes_json};
        const edgesData = {edges_json};
        const highlights = {highlights_json};
        const patterns = {patterns_json};
        
        // Create vis.js nodes and edges
        const nodes = new vis.DataSet(nodesData.map(node => ({{
            id: node.id,
            label: node.label,
            title: `${{node.label}}\\nType: ${{node.type}}\\nRisk: ${{node.riskscore.toFixed(2)}}`,
            color: {{
                background: node.color,
                border: node.color,
                highlight: {{
                    background: '#FFD700',
                    border: '#FFA500'
                }}
            }},
            size: node.size,
            font: {{
                size: 12,
                color: '#2c3e50'
            }},
            originalColor: node.color
        }})));
        
        const edges = new vis.DataSet(edgesData.map((edge, idx) => ({{
            id: idx,
            from: nodesData[edge.from].id,
            to: nodesData[edge.to].id,
            label: edge.label,
            title: edge.label,
            width: edge.width,
            color: {{
                color: '#95a5a6',
                highlight: '#e74c3c'
            }},
            arrows: 'to',
            font: {{
                size: 10,
                align: 'middle'
            }}
        }})));
        
        // Network configuration
        const container = document.getElementById('network-container');
        const data = {{ nodes, edges }};
        const options = {{
            nodes: {{
                shape: 'dot',
                borderWidth: 2,
                shadow: true
            }},
            edges: {{
                smooth: {{
                    type: 'continuous'
                }},
                shadow: true
            }},
            physics: {{
                enabled: true,
                stabilization: {{
                    iterations: 200
                }},
                barnesHut: {{
                    gravitationalConstant: -8000,
                    centralGravity: 0.3,
                    springLength: 150,
                    springConstant: 0.04
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 100,
                navigationButtons: true,
                keyboard: true
            }}
        }};
        
        // Create network
        const network = new vis.Network(container, data, options);
        
        // Pattern highlighting functions
        let currentHighlight = null;
        
        function highlightPattern(patternType) {{
            resetView();
            
            const button = document.getElementById(`highlight-${{patternType}}`);
            button.classList.add('active');
            currentHighlight = patternType;
            
            let highlightNodes = [];
            
            if (patternType === 'shell' && highlights.shell_chains.length > 0) {{
                highlights.shell_chains.forEach(chain => {{
                    highlightNodes = highlightNodes.concat(chain.nodes.map(idx => nodesData[idx].id));
                }});
            }} else if (patternType === 'circular' && highlights.circular_cycles.length > 0) {{
                highlights.circular_cycles.forEach(cycle => {{
                    highlightNodes = highlightNodes.concat(cycle.nodes.map(idx => nodesData[idx].id));
                }});
            }} else if (patternType === 'hidden' && highlights.hidden_influence.length > 0) {{
                highlights.hidden_influence.forEach(hidden => {{
                    highlightNodes = highlightNodes.concat(hidden.nodes.map(idx => nodesData[idx].id));
                }});
            }}
            
            if (highlightNodes.length > 0) {{
                // Dim all nodes first
                nodes.forEach(node => {{
                    nodes.update({{
                        id: node.id,
                        color: {{
                            background: '#e0e0e0',
                            border: '#bdbdbd'
                        }}
                    }});
                }});
                
                // Highlight selected nodes
                highlightNodes.forEach(nodeId => {{
                    const node = nodes.get(nodeId);
                    if (node) {{
                        nodes.update({{
                            id: nodeId,
                            color: {{
                                background: '#FFD700',
                                border: '#FFA500'
                            }},
                            size: (node.size || 15) * 1.3
                        }});
                    }}
                }});
                
                // Fit view to highlighted nodes
                network.fit({{
                    nodes: highlightNodes,
                    animation: true
                }});
            }}
        }}
        
        function resetView() {{
            // Remove active class from all buttons
            document.querySelectorAll('.controls button').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            currentHighlight = null;
            
            // Restore original colors
            nodes.forEach(node => {{
                const originalNode = nodesData.find(n => n.id === node.id);
                if (originalNode) {{
                    nodes.update({{
                        id: node.id,
                        color: {{
                            background: originalNode.color,
                            border: originalNode.color
                        }},
                        size: originalNode.size
                    }});
                }}
            }});
            
            network.fit({{ animation: true }});
        }}
        
        // Populate pattern details
        function populatePatterns() {{
            // Shell chains
            const shellContainer = document.getElementById('shell-patterns');
            if (patterns.shell_chains.length === 0) {{
                shellContainer.innerHTML = '<div class="no-patterns">No shell chains detected</div>';
            }} else {{
                shellContainer.innerHTML = patterns.shell_chains.map((pattern, idx) => `
                    <div class="pattern-item">
                        <strong>Chain ${{idx + 1}}</strong>
                        <span class="badge high-risk">Risk: ${{pattern.riskScore}}</span>
                        <br>Length: ${{pattern.chainLength}} companies
                        <br>Auditor: ${{pattern.auditorId}}
                        <br>Avg Invoices: ${{pattern.avgInvoices}}
                    </div>
                `).join('');
            }}
            
            // Circular trade
            const circularContainer = document.getElementById('circular-patterns');
            if (patterns.circular_trade.length === 0) {{
                circularContainer.innerHTML = '<div class="no-patterns">No circular trade detected</div>';
            }} else {{
                circularContainer.innerHTML = patterns.circular_trade.map((pattern, idx) => `
                    <div class="pattern-item">
                        <strong>Cycle ${{idx + 1}}</strong>
                        <span class="badge ${{pattern.riskScore >= 0.7 ? 'high-risk' : 'medium-risk'}}">
                            Risk: ${{pattern.riskScore.toFixed(2)}}
                        </span>
                        <br>Volume: $${{pattern.totalVolume.toFixed(0)}}M
                        <br>Isolation: ${{(pattern.isolationScore * 100).toFixed(1)}}%
                        <br>Companies: ${{pattern.cycle.join(' → ')}}
                    </div>
                `).join('');
            }}
            
            // Hidden influence
            const hiddenContainer = document.getElementById('hidden-patterns');
            if (patterns.hidden_influence.length === 0) {{
                hiddenContainer.innerHTML = '<div class="no-patterns">No hidden influence detected</div>';
            }} else {{
                hiddenContainer.innerHTML = patterns.hidden_influence.map((pattern, idx) => `
                    <div class="pattern-item">
                        <strong>Pattern ${{idx + 1}}</strong>
                        <span class="badge low-risk">Opp: ${{pattern.opportunityScore.toFixed(2)}}</span>
                        <br>Shareholder: ${{pattern.shareholderId}}
                        <br>Via Supplier: ${{pattern.supplierId}}
                        <br>Concentration: ${{pattern.concentrationPct.toFixed(1)}}%
                        <br>Ownership: ${{pattern.ownershipPct.toFixed(1)}}%
                    </div>
                `).join('');
            }}
        }}
        
        // Initialize
        network.on('stabilizationIterationsDone', function() {{
            network.setOptions({{ physics: false }});
        }});
        
        populatePatterns();
    </script>
</body>
</html>"""
        
        return html


def create_visualization_for_company(
    company_id: str,
    neo4j_uri: str = "bolt://localhost:7687",
    neo4j_user: str = "neo4j",
    neo4j_password: str = "password",
    output_path: str = None
) -> str:
    """
    Convenience function to create visualization for a company.
    
    Args:
        company_id: Company ID to visualize
        neo4j_uri: Neo4j connection URI
        neo4j_user: Neo4j username
        neo4j_password: Neo4j password
        output_path: Output path for HTML file
        
    Returns:
        Path to generated HTML file
    """
    if output_path is None:
        output_path = f'fraud_network_{company_id}.html'
    
    visualizer = FraudNetworkVisualizer(neo4j_uri, neo4j_user, neo4j_password)
    try:
        return visualizer.generate_html_visualization(company_id, output_path)
    finally:
        visualizer.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        company_id = sys.argv[1]
    else:
        company_id = "c32"  # Default test company
    
    output_file = create_visualization_for_company(company_id)
    print(f"Visualization generated: {output_file}")
    print(f"Open {output_file} in your browser to view the network.")
