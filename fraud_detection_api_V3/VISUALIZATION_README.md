# Fraud Detection Network Visualization 🔍

Interactive network visualization for fraud detection patterns using Python, NetworkX, and Vis.js.

## Features

### ✨ Core Capabilities

1. **2-Hop Network Visualization**
   - Displays the queried company and all entities within 2 relationship steps
   - Shows companies, shareholders, auditors, and their connections
   - Interactive pan, zoom, and hover tooltips

2. **Risk-Based Visual Encoding**
   - **Node Colors:**
     - 🔴 Red: High risk (≥0.7)
     - 🟠 Orange: Medium risk (0.4-0.7)
     - 🟢 Green: Low risk (<0.4)
     - 🔵 Blue: Query company (center node)
   - **Node Sizes:** Larger nodes = lower risk (more legitimate)
   - **Edge Widths:** Based on transaction volume or ownership percentage

3. **Pattern Highlighting**
   - **🔗 Shell Company Chains:** Highlights suspicious subsidiary chains with high-risk auditors
   - **🔄 Circular Trade:** Highlights circular trading patterns between companies
   - **👁️ Hidden Influence:** Highlights undisclosed shareholder influence patterns

4. **Interactive Controls**
   - Pattern-specific highlighting buttons
   - Reset view to see full network
   - Hover for detailed node information
   - Click and drag to explore

5. **Statistics Dashboard**
   - Overall risk score
   - Opportunity score
   - Total entities and relationships
   - High-risk node count

6. **Pattern Details Sidebar**
   - Detailed information for each detected pattern
   - Risk scores, volumes, and key metrics
   - Entity identifiers and relationships

## Installation

### Prerequisites

- Python 3.8+
- Neo4j database with fraud detection schema
- Required Python packages:

```bash
pip install networkx neo4j fastapi uvicorn
```

### Files Required

- `visualization.py` - Main visualization module
- `fraud_engine.py` - Fraud detection engine
- `app.py` - FastAPI application (optional, for API endpoint)
- `run_visualization.py` - Standalone runner script

## Usage

### Method 1: Standalone Script (Recommended)

Generate visualization for a specific company:

```bash
python run_visualization.py c32
```

With custom output file:

```bash
python run_visualization.py c32 -o my_analysis.html
```

With custom Neo4j connection:

```bash
python run_visualization.py c32 \
  --neo4j-uri bolt://localhost:7687 \
  --neo4j-user neo4j \
  --neo4j-password mypassword
```

### Method 2: Python Script

```python
from visualization import create_visualization_for_company

# Generate visualization
output_file = create_visualization_for_company(
    company_id='c32',
    neo4j_uri='bolt://localhost:7687',
    neo4j_user='neo4j',
    neo4j_password='password'
)

print(f"Open {output_file} in your browser")
```

### Method 3: API Endpoint

If using the FastAPI integration:

```bash
# Start the server
uvicorn app:app --reload

# Access visualization in browser
http://localhost:8000/company/c32/visualize
```

Or get JSON data:

```bash
curl http://localhost:8000/company/c32
```

## Output

The visualization generates a self-contained HTML file that can be:
- Opened in any modern web browser
- Shared with stakeholders
- Embedded in reports
- No internet connection required (all assets embedded)

### Sample Output Structure

```
fraud_network_c32.html
├── Interactive network graph (center)
├── Control buttons (top-left)
├── Statistics dashboard (top)
└── Pattern details sidebar (right)
```

## Visualization Components

### Network Graph

The main network visualization uses **Vis.js** for rendering:

- **Physics simulation:** Nodes automatically arrange for optimal viewing
- **Smooth edges:** Curved connections for clarity
- **Interactive tooltips:** Hover to see entity details
- **Zoom controls:** Mouse wheel or buttons
- **Pan:** Click and drag background
- **Node selection:** Click nodes for details

### Pattern Highlighting

Click the control buttons to highlight specific patterns:

#### 1. Shell Company Chains 🔗
- Highlights all companies in detected subsidiary chains
- Shows high-risk auditor connections
- Displays chain length and invoice statistics

#### 2. Circular Trade 🔄
- Highlights companies in circular trading patterns
- Shows trade volume and cycle length
- Displays isolation score (how closed the cycle is)

#### 3. Hidden Influence 👁️
- Highlights undisclosed shareholder relationships
- Shows concentration percentages
- Displays influence scores from PageRank

### Statistics Panel

Top-bar metrics provide quick insights:

- **Risk Score:** Overall fraud risk (0-1 scale)
- **Opportunity Score:** Business opportunity potential
- **Total Entities:** Number of nodes in network
- **Relationships:** Number of connections
- **High Risk Nodes:** Count of entities with risk ≥0.7

## Customization

### Modify Colors

Edit the color scheme in `visualization.py`:

```python
# High risk
if risk >= 0.7:
    color = '#E74C3C'  # Red
# Medium risk
elif risk >= 0.4:
    color = '#F39C12'  # Orange
# Low risk
else:
    color = '#27AE60'  # Green
```

### Adjust Node Sizes

Modify size calculation:

```python
size = max(10.0, 25.0 - risk * 15.0)
```

### Change Layout Physics

Edit the physics settings in the HTML template:

```javascript
physics: {
    barnesHut: {
        gravitationalConstant: -8000,  // Repulsion strength
        centralGravity: 0.3,            // Center pull
        springLength: 150,              // Edge length
        springConstant: 0.04            // Edge stiffness
    }
}
```

## Technical Architecture

### Data Flow

```
Neo4j Database
    ↓
FraudDetectionEngine (fraud_engine.py)
    ↓
FraudNetworkVisualizer (visualization.py)
    ↓
NetworkX Graph + Pattern Analysis
    ↓
HTML + Vis.js Visualization
    ↓
Interactive Browser Display
```

### Key Classes

#### `FraudNetworkVisualizer`

Main visualization class with methods:

- `build_network_graph()`: Creates NetworkX graph from Neo4j data
- `_get_2hop_neighborhood()`: Queries Neo4j for 2-hop network
- `_identify_pattern_highlights()`: Maps detected patterns to nodes
- `generate_html_visualization()`: Creates interactive HTML file
- `_generate_html_template()`: Builds HTML with embedded Vis.js

### Dependencies

| Library | Purpose |
|---------|---------|
| NetworkX | Graph data structure and analysis |
| Neo4j Driver | Database connectivity |
| Vis.js | Interactive network rendering |
| FastAPI | Optional API endpoint |

## Troubleshooting

### Common Issues

**1. "No module named 'networkx'"**
```bash
pip install networkx
```

**2. "Failed to connect to Neo4j"**
- Check Neo4j is running: `systemctl status neo4j`
- Verify connection details in environment variables
- Test connection: `cypher-shell -u neo4j -p password`

**3. "No data displayed"**
- Verify company_id exists: `MATCH (c:Company {company_id: 'c32'}) RETURN c`
- Check relationship connections exist
- Review logs for errors

**4. "Visualization looks empty"**
- Company may have no connections
- Try a different company_id
- Check 2-hop query returns results

**5. "Pattern buttons don't highlight anything"**
- Patterns may not be detected for this company
- Check pattern detection thresholds
- Review sidebar for pattern details

## Performance Considerations

- **Large Networks (>500 nodes):** May load slowly, consider filtering
- **Physics Simulation:** Disable after stabilization for better performance
- **Pattern Highlighting:** Only active patterns are computed
- **Memory Usage:** Proportional to network size

## Best Practices

1. **Start with Known Fraud Cases:** Test with companies that have known patterns
2. **Compare Multiple Companies:** Generate visualizations for comparison
3. **Export for Reports:** HTML files can be embedded or printed
4. **Adjust Thresholds:** Modify pattern detection parameters based on results
5. **Use Pattern Highlighting:** Focus on specific fraud types during review

## API Integration

### FastAPI Endpoints

```python
# Get visualization HTML
GET /company/{company_id}/visualize

# Get JSON data
GET /company/{company_id}

# Health check
GET /health
```

### Response Format

JSON endpoint returns:

```json
{
  "riskscore": 0.85,
  "opportunityscore": 0.42,
  "patterns": {
    "pattern1_shell": [...],
    "pattern2_circular": [...],
    "pattern3_hidden": [...]
  },
  "visualizationdata": {
    "nodes": [...],
    "edges": [...]
  }
}
```

## Examples

### Example 1: High-Risk Company Analysis

```bash
python run_visualization.py c32
```

Expected output:
- Red/orange nodes indicating high risk
- Multiple pattern highlights available
- Detailed metrics in sidebar

### Example 2: Clean Company (No Patterns)

```bash
python run_visualization.py c150
```

Expected output:
- Mostly green nodes
- "No patterns detected" in sidebar
- Low risk score

### Example 3: Batch Processing

```python
from visualization import create_visualization_for_company

companies = ['c32', 'c45', 'c78', 'c100']

for company_id in companies:
    output = create_visualization_for_company(company_id)
    print(f"Generated: {output}")
```

## License

This visualization module is part of the Fraud Detection System.

## Support

For issues or questions:
1. Check this README
2. Review the code comments
3. Test with known working company IDs
4. Check Neo4j query execution

## Future Enhancements

Potential improvements:

- [ ] Export to PDF/PNG
- [ ] Time-series animation
- [ ] Multi-company comparison view
- [ ] Custom pattern definitions
- [ ] Risk score heatmaps
- [ ] Graph clustering visualization
- [ ] Real-time updates via WebSocket
- [ ] Mobile-responsive design
- [ ] Dark mode theme
