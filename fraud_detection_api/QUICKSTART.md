# Quick Start Guide - Fraud Detection Network Visualization

## 🚀 Quick Setup (5 minutes)

### Step 1: Verify Prerequisites

```bash
# Check Python version (need 3.8+)
python --version

# Check Neo4j is running
systemctl status neo4j  # Linux
# OR check if Neo4j Desktop is running

# Test Neo4j connection
echo "MATCH (n) RETURN count(n)" | cypher-shell -u neo4j -p password
```

### Step 2: Install Dependencies

```bash
# Install required packages
pip install networkx neo4j fastapi uvicorn

# Verify installation
python -c "import networkx; import neo4j; print('✅ All packages installed')"
```

### Step 3: Configure Environment (Optional)

```bash
# Set environment variables
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your_password"
```

Or create a `.env` file:

```bash
cat > .env << EOF
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
EOF
```

### Step 4: Generate Your First Visualization

```bash
# Generate visualization for company c32
python run_visualization.py c32

# Open the generated HTML file in your browser
# The script will show you the file path
```

**Expected output:**
```
🔍 Generating visualization for company: c32
📊 Connecting to Neo4j at: bolt://localhost:7687
✅ Visualization generated successfully!
📁 Output file: fraud_network_c32.html

🌐 Open the file in your browser to view the interactive network:
   file:///path/to/fraud_network_c32.html
```

---

## 📋 Three Ways to Use the Visualization

### Method 1: Command Line (Simplest)

```bash
# Basic usage
python run_visualization.py c32

# Custom output file
python run_visualization.py c32 -o my_analysis.html

# Different company
python run_visualization.py c100

# Custom Neo4j connection
python run_visualization.py c32 \
  --neo4j-uri bolt://localhost:7687 \
  --neo4j-user neo4j \
  --neo4j-password mypassword
```

### Method 2: Python Script

Create a file `my_analysis.py`:

```python
from visualization import create_visualization_for_company

# Generate visualization
output = create_visualization_for_company(
    company_id='c32',
    neo4j_uri='bolt://localhost:7687',
    neo4j_user='neo4j',
    neo4j_password='password'
)

print(f"Visualization created: {output}")
```

Run it:
```bash
python my_analysis.py
```

### Method 3: API Endpoint (Most Flexible)

```bash
# Start the FastAPI server
uvicorn app:app --reload --port 8000

# In another terminal or browser:
# Get interactive visualization
curl http://localhost:8000/company/c32/visualize > viz.html

# Get JSON data
curl http://localhost:8000/company/c32 | jq

# Open in browser
open http://localhost:8000/company/c32/visualize
```

---

## 🎯 Usage Examples

### Example 1: Analyze Single Company

```bash
python run_visualization.py c32
```

Open `fraud_network_c32.html` in your browser. You'll see:
- Network graph with color-coded risk levels
- Interactive pattern highlighting buttons
- Statistics dashboard
- Detailed pattern information

### Example 2: Batch Analysis

Create `batch_analysis.py`:

```python
from visualization import create_visualization_for_company

companies = ['c32', 'c45', 'c78', 'c100', 'c150']

for company_id in companies:
    try:
        output = create_visualization_for_company(company_id)
        print(f"✅ {company_id}: {output}")
    except Exception as e:
        print(f"❌ {company_id}: {str(e)}")
```

Run it:
```bash
python batch_analysis.py
```

### Example 3: Programmatic Analysis

```python
from visualization import FraudNetworkVisualizer

# Initialize
viz = FraudNetworkVisualizer(
    neo4j_uri='bolt://localhost:7687',
    neo4j_user='neo4j',
    neo4j_password='password'
)

try:
    # Get network data
    network = viz.build_network_graph('c32')
    
    # Access data
    print(f"Risk Score: {network['risk_score']}")
    print(f"Nodes: {network['stats']['total_nodes']}")
    print(f"High Risk: {network['stats']['high_risk_nodes']}")
    
    # Generate HTML
    viz.generate_html_visualization('c32', 'output.html')
    
finally:
    viz.close()
```

---

## 🔍 Understanding the Visualization

### Color Coding

| Color | Risk Level | Meaning |
|-------|-----------|---------|
| 🔴 Red | High (≥0.7) | Significant fraud risk |
| 🟠 Orange | Medium (0.4-0.7) | Moderate fraud risk |
| 🟢 Green | Low (<0.4) | Low fraud risk |
| 🔵 Blue | N/A | Query company (center) |

### Pattern Buttons

Click these buttons to highlight detected patterns:

1. **🔗 Shell Chains** - Highlights suspicious subsidiary chains
2. **🔄 Circular Trade** - Highlights circular trading patterns
3. **👁️ Hidden Influence** - Highlights undisclosed shareholder influence
4. **↺ Reset View** - Return to full network view

### Node Sizes

- **Larger nodes** = Lower risk (more legitimate entities)
- **Smaller nodes** = Higher risk (suspicious entities)

### Edge Widths

- **Thicker edges** = Higher transaction volume or ownership percentage
- **Thinner edges** = Lower transaction volume or ownership percentage

---

## 🛠️ Troubleshooting

### Problem: "No module named 'networkx'"

**Solution:**
```bash
pip install networkx neo4j
```

### Problem: "Failed to connect to Neo4j"

**Solution:**
```bash
# Check Neo4j is running
systemctl status neo4j

# Test connection
cypher-shell -u neo4j -p password

# Verify credentials
export NEO4J_PASSWORD="your_actual_password"
```

### Problem: "Company not found"

**Solution:**
```bash
# Verify company exists in database
echo "MATCH (c:Company {company_id: 'c32'}) RETURN c" | cypher-shell -u neo4j -p password

# Try a different company ID
python run_visualization.py c100
```

### Problem: "Visualization is empty"

**Solution:**
- Company may have no connections
- Try different company: `python run_visualization.py c45`
- Check database has relationships: `MATCH ()-[r]->() RETURN count(r)`

### Problem: "Pattern buttons don't work"

**Solution:**
- Patterns may not exist for this company
- Check sidebar for pattern details
- Try a company with known fraud patterns

---

## 📊 API Reference

### REST Endpoints

#### Get Visualization HTML
```
GET /company/{company_id}/visualize
```

**Response:** HTML page with interactive visualization

**Example:**
```bash
curl http://localhost:8000/company/c32/visualize > viz.html
```

#### Get Analysis Data (JSON)
```
GET /company/{company_id}
```

**Response:**
```json
{
  "riskscore": 0.85,
  "opportunityscore": 0.42,
  "patterns": {
    "pattern1_shell": [],
    "pattern2_circular": [],
    "pattern3_hidden": []
  },
  "visualizationdata": {
    "nodes": [],
    "edges": []
  }
}
```

**Example:**
```bash
curl http://localhost:8000/company/c32 | jq '.riskscore'
```

#### Health Check
```
GET /health
```

**Response:**
```json
{"status": "healthy"}
```

---

## 📁 File Structure

```
fraud-detection/
├── app.py                      # FastAPI application
├── fraud_engine.py             # Core fraud detection engine
├── visualization.py            # Visualization module
├── run_visualization.py        # Command-line runner
├── demo_visualization.py       # Demo script
├── VISUALIZATION_README.md     # Detailed documentation
└── QUICKSTART.md              # This file
```

---

## 🎓 Next Steps

1. **Explore the Demo:**
   ```bash
   python demo_visualization.py
   ```

2. **Read Full Documentation:**
   Open `VISUALIZATION_README.md` for detailed information

3. **Customize Visualizations:**
   Edit color schemes, sizes, and layouts in `visualization.py`

4. **Integrate with Your Workflow:**
   Use the API endpoints in your applications

5. **Batch Process Multiple Companies:**
   Create scripts to analyze multiple companies at once

---

## 💡 Tips for Best Results

1. **Start with Known Cases:** Test with companies that have known fraud patterns
2. **Use Pattern Highlighting:** Focus on specific fraud types during analysis
3. **Compare Multiple Companies:** Generate visualizations side-by-side
4. **Adjust Thresholds:** Modify pattern detection parameters based on your needs
5. **Export and Share:** HTML files are self-contained and easy to share

---

## 📞 Getting Help

If you encounter issues:

1. Check this Quick Start guide
2. Read `VISUALIZATION_README.md` for detailed documentation
3. Run `python demo_visualization.py` to see working examples
4. Verify your Neo4j connection and data
5. Check Python package versions: `pip list | grep -E "(networkx|neo4j)"`

---

## ✅ Success Checklist

- [ ] Python 3.8+ installed
- [ ] Neo4j database running and accessible
- [ ] Required packages installed (`networkx`, `neo4j`)
- [ ] Successfully generated first visualization
- [ ] Can open HTML file in browser
- [ ] Interactive controls working
- [ ] Pattern highlighting functioning
- [ ] Can access via API (optional)

**Congratulations! You're ready to detect fraud patterns! 🎉**
