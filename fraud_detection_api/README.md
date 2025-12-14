# 🔍 Fraud Detection Network Visualization - Complete Solution

**Interactive Web Interface + FastAPI Backend + Neo4j Integration**

## 🎯 What This Is

A complete, production-ready system for visualizing and analyzing company fraud patterns through an interactive web interface. Users enter a company ID, and the system:

1. ✅ Queries Neo4j database for the company's network
2. ✅ Detects fraud patterns (Shell Chains, Circular Trade, Hidden Influence)
3. ✅ Builds an interactive 2-hop network visualization
4. ✅ Color-codes nodes by risk level
5. ✅ Allows pattern highlighting with interactive buttons
6. ✅ Displays detailed metrics and statistics

---

## 🚀 Quick Start (3 Steps - 2 Minutes)

### Option 1: Automated Startup (Easiest)

```bash
# 1. Make sure Neo4j is running
# 2. Run the startup script
chmod +x start.sh
./start.sh
```

**That's it!** The script will:
- Install dependencies
- Start FastAPI server
- Open the web interface in your browser

### Option 2: Manual Startup

```bash
# Step 1: Install dependencies
pip install uvicorn fastapi networkx neo4j --break-system-packages

# Step 2: Start FastAPI server
uvicorn app:app --reload --port 8000

# Step 3: Open web interface
open fraud_viewer.html  # macOS
# OR double-click fraud_viewer.html
```

---

## 📁 What You Get (10 Files)

### 🌐 Web Interface
1. **`fraud_viewer.html`** - Interactive web interface
   - Enter company ID
   - View network visualization
   - Highlight fraud patterns
   - See detailed statistics

### 🔧 Backend Components
2. **`app.py`** - FastAPI application with endpoints
3. **`fraud_engine.py`** - Fraud detection logic (all bugs fixed)
4. **`visualization.py`** - Network visualization module

### 🛠️ Utilities
5. **`start.sh`** - One-click startup script
6. **`run_visualization.py`** - CLI tool for offline HTML generation
7. **`demo_visualization.py`** - Demo suite with examples

### 📚 Documentation
8. **`WEB_INTERFACE_GUIDE.md`** - Web interface usage guide
9. **`QUICKSTART.md`** - Quick setup guide
10. **`VISUALIZATION_README.md`** - Complete documentation

---

## 🎨 Features

### Interactive Web Interface
- **Search by Company ID**: Simple input field
- **Real-time Analysis**: Fetches data from FastAPI
- **Interactive Network Graph**: Pan, zoom, hover tooltips
- **Pattern Highlighting**: Click buttons to highlight patterns
- **Statistics Dashboard**: Risk scores, entity counts, metrics
- **Pattern Details**: Sidebar with detailed information
- **Responsive Design**: Works on desktop and tablet

### Visual Encoding
- **🔴 Red nodes**: High risk (≥0.7)
- **🟠 Orange nodes**: Medium risk (0.4-0.7)
- **🟢 Green nodes**: Low risk (<0.4)
- **🔵 Blue node**: Query company (center)
- **Node sizes**: Larger = lower risk
- **Edge widths**: Thicker = higher volume/ownership

### Pattern Detection
- **🔗 Shell Company Chains**: Long subsidiary chains with suspicious auditors
- **🔄 Circular Trade**: Closed trading loops between companies
- **👁️ Hidden Influence**: Undisclosed shareholder control

---

## 💻 How to Use

### Basic Workflow

1. **Start the system**
   ```bash
   ./start.sh
   ```

2. **Web interface opens automatically**
   - Default company: `c32`
   - Change to any company ID

3. **Click "Analyze"**
   - System fetches data from FastAPI
   - Builds network visualization
   - Detects fraud patterns

4. **Explore the results**
   - View statistics at top
   - Examine network graph
   - Click pattern buttons
   - Read pattern details in sidebar

5. **Try different companies**
   - Enter new company ID
   - Click "Analyze" again
   - Compare patterns

### Pattern Highlighting

Click these buttons to focus on specific fraud types:

- **🔗 Shell Chains**: Highlights companies in suspicious subsidiary chains
- **🔄 Circular Trade**: Highlights companies in circular trading patterns  
- **👁️ Hidden Influence**: Highlights undisclosed shareholder relationships
- **↺ Reset View**: Return to full network view

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           Web Browser (fraud_viewer.html)       │
│  - Company ID input                             │
│  - Interactive network (Vis.js)                 │
│  - Pattern highlighting                         │
│  - Statistics dashboard                         │
└────────────────┬────────────────────────────────┘
                 │ HTTP Request
                 │ GET /company/{id}
                 ↓
┌─────────────────────────────────────────────────┐
│         FastAPI Backend (app.py)                │
│  - API endpoints                                │
│  - Request validation                           │
│  - Response formatting                          │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│    Fraud Detection Engine (fraud_engine.py)     │
│  - Pattern 1: Shell company chains              │
│  - Pattern 2: Circular trade                    │
│  - Pattern 3: Hidden influence                  │
│  - 2-hop neighborhood queries                   │
└────────────────┬────────────────────────────────┘
                 │ Cypher Queries
                 ↓
┌─────────────────────────────────────────────────┐
│              Neo4j Database                     │
│  - Companies, Shareholders, Auditors            │
│  - Relationships: SUPPLIES, OWNS_SHARE, etc.    │
│  - Invoices and transactions                    │
└─────────────────────────────────────────────────┘
```

---

## 🔌 API Endpoints

### GET `/company/{company_id}`

Returns fraud analysis data for visualization.

**Response:**
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

### GET `/company/{company_id}/visualize`

Returns complete HTML visualization (for standalone use).

### GET `/health`

Health check endpoint.

**API Documentation:** http://localhost:8000/docs

---

## 🎯 Usage Examples

### Example 1: Analyze High-Risk Company

```
1. Open fraud_viewer.html
2. Enter: c32
3. Click: Analyze
4. Click: "Shell Chains" button
5. Review: Detected patterns in sidebar
```

**Expected Result:**
- Red/orange nodes indicating high risk
- Highlighted subsidiary chains
- Detailed metrics showing suspicious patterns

### Example 2: Compare Multiple Companies

```
1. Analyze c32 (take screenshot)
2. Analyze c45 (take screenshot)
3. Analyze c100 (take screenshot)
4. Compare patterns side-by-side
```

### Example 3: Export Results

```
1. Analyze company
2. Take screenshot (Cmd/Ctrl + Shift + S)
3. Right-click → "Save Page As"
4. Include in report
```

---

## 🔧 Configuration

### Change API Endpoint

In `fraud_viewer.html`, modify the API endpoint field:
- Default: `http://localhost:8000`
- Custom: `http://your-server:port`

### Change Neo4j Connection

In `app.py`, set environment variables:
```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your_password"
```

Or edit directly in `app.py`:
```python
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password"
```

---

## 🐛 Troubleshooting

### Problem: Web interface shows error

**Solution:**
```bash
# Check FastAPI is running
curl http://localhost:8000/health

# Should return: {"status":"healthy"}

# If not, start it:
uvicorn app:app --reload --port 8000
```

### Problem: "Company not found"

**Solution:**
```bash
# List available companies in Neo4j
echo "MATCH (c:Company) RETURN c.company_id LIMIT 10" | cypher-shell -u neo4j -p password

# Try one of the listed companies
```

### Problem: No patterns highlighted

**This is normal!** Not all companies have detectable fraud patterns. Try:
- `c32` - Known to have some patterns
- Different company IDs
- Check sidebar - it will say "No patterns detected" if none exist

### Problem: Network graph is blank

**Possible causes:**
1. Company has no connections (normal for some companies)
2. Neo4j connection issue (check logs)
3. JavaScript error (check browser console with F12)

---

## 📊 Understanding the Results

### Risk Score (0-1 scale)
- **0.0 - 0.3**: Low risk (likely legitimate)
- **0.4 - 0.6**: Medium risk (worth investigating)
- **0.7 - 1.0**: High risk (strong fraud indicators)

### Pattern Types

| Pattern | Indicator | Risk Level |
|---------|-----------|------------|
| Shell Chains | Long subsidiary chains, high-risk auditors | High |
| Circular Trade | Closed trading loops, high isolation | High |
| Hidden Influence | Undisclosed shareholder control | Medium-High |

### Node Colors

| Color | Meaning | Action |
|-------|---------|--------|
| 🔴 Red | High risk | Investigate immediately |
| 🟠 Orange | Medium risk | Monitor closely |
| 🟢 Green | Low risk | Routine checks |
| 🔵 Blue | Query company | Analysis subject |

---

## 🚀 Advanced Usage

### Offline HTML Generation

Generate standalone HTML files without the web interface:

```bash
python run_visualization.py c32
# Opens: fraud_network_c32.html
```

### Batch Processing

```python
from visualization import create_visualization_for_company

companies = ['c32', 'c45', 'c78', 'c100']
for company_id in companies:
    create_visualization_for_company(company_id)
```

### Custom Analysis

```python
from fraud_engine import FraudDetectionEngine

engine = FraudDetectionEngine(
    'bolt://localhost:7687',
    'neo4j',
    'password'
)

risk, opportunity, patterns = engine.analyze_company('c32')
print(f"Risk: {risk}, Opportunity: {opportunity}")
engine.close()
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **WEB_INTERFACE_GUIDE.md** | How to use the web interface |
| **QUICKSTART.md** | Quick setup and basic usage |
| **VISUALIZATION_README.md** | Complete technical documentation |
| **PROJECT_SUMMARY.md** | Project overview and architecture |

---

## ✅ System Requirements

### Software
- Python 3.8+
- Neo4j 4.0+ (with GDS library)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Python Packages
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `neo4j` - Database driver
- `networkx` - Graph library

### Hardware
- 4GB RAM minimum (8GB recommended for large networks)
- Network access to Neo4j database

---

## 🎓 Learning Resources

### Quick Start
1. Read `WEB_INTERFACE_GUIDE.md`
2. Run `./start.sh`
3. Try analyzing `c32`
4. Experiment with different companies

### Deep Dive
1. Read `VISUALIZATION_README.md`
2. Study `fraud_engine.py` for pattern logic
3. Review `visualization.py` for rendering
4. Explore API at `http://localhost:8000/docs`

---

## 🎉 What Makes This Special

### ✅ Complete Solution
- Web interface + Backend + Database integration
- No manual file management
- Real-time analysis

### ✅ User-Friendly
- Simple company ID input
- Interactive visualization
- Clear pattern highlighting
- Detailed explanations

### ✅ Production-Ready
- Error handling
- Loading indicators
- Responsive design
- Comprehensive documentation

### ✅ Extensible
- Modular architecture
- REST API
- Custom pattern support
- Easy integration

---

## 🏆 Success Checklist

Before starting:
- [ ] Neo4j database is running
- [ ] Have company IDs to analyze
- [ ] Basic understanding of fraud patterns

After setup:
- [ ] FastAPI server responds at http://localhost:8000/health
- [ ] Web interface opens in browser
- [ ] Can enter company ID and click Analyze
- [ ] Network graph displays
- [ ] Pattern buttons work
- [ ] Statistics show correct values

---

## 📞 Support

### Check These First
1. **WEB_INTERFACE_GUIDE.md** - Usage instructions
2. **Browser console** (F12) - JavaScript errors
3. **FastAPI logs** - Backend errors
4. **Neo4j logs** - Database issues

### Common Issues
- **Connection refused**: Start FastAPI server
- **No data**: Check company ID exists
- **Slow loading**: Normal for large networks
- **No patterns**: Company may be clean

---

## 🎯 Next Steps

1. **Explore** - Try different company IDs
2. **Compare** - Analyze multiple companies
3. **Customize** - Adjust colors, sizes, thresholds
4. **Integrate** - Connect to your workflow
5. **Extend** - Add new pattern types

---

## 📝 Quick Command Reference

```bash
# Start everything
./start.sh

# Start manually
uvicorn app:app --reload --port 8000

# Generate offline HTML
python run_visualization.py c32

# Run demos
python demo_visualization.py

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/company/c32

# Stop server
Ctrl + C
```

---
