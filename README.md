# 🕵️ Fraud Detection System
### Graph-Based Pattern Analysis using Neo4j & FastAPI

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-008CC1?style=flat&logo=neo4j&logoColor=white)](https://neo4j.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=flat&logo=jupyter&logoColor=white)](https://jupyter.org/)

An advanced fraud detection system that leverages graph algorithms to identify suspicious patterns in financial networks. This project uses Neo4j graph database, FastAPI backend, and an interactive web interface to detect three types of fraud patterns: Shell Company Chains, Circular Trade, and Hidden Influence.

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Project Structure](#-project-structure)
- [Usage Guide](#-usage-guide)
  - [Part 1: Data Generation](#part-1-data-generation-notebooks)
  - [Part 2: Data Ingestion](#part-2-data-ingestion-to-neo4j)
  - [Part 3: Fraud Pattern Detection](#part-3-fraud-pattern-detection-complete-network)
  - [Part 4: Fraud Detection API](#part-4-fraud-detection-api--ui)
- [Fraud Patterns Explained](#-fraud-patterns-explained)
- [API Reference](#-api-reference)
- [Technologies Used](#-technologies-used)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

This fraud detection system analyzes financial networks to identify three critical fraud patterns:

1. **🔗 Shell Company Chains**: Detects suspicious subsidiary chains with shared high-risk auditors
2. **🔄 Circular Trade**: Identifies closed loops of transactions indicating revenue inflation
3. **👤 Hidden Influence**: Discovers indirect control through concentrated supplier relationships

The system operates in two modes:
- **Batch Analysis**: Analyzes the entire network using Jupyter notebooks
- **Real-time Query**: Interactive web interface for company-specific analysis

---

## ✨ Features

### 🔍 Advanced Fraud Detection
- **Three Pattern Detection Algorithms**
  - Shell Company Detection (Graph Traversal)
  - Circular Trade Detection (Cycle Detection)  
  - Hidden Influence Detection (PageRank + Multi-hop Analysis)

### 📊 Interactive Visualization
- Real-time graph network visualization
- Color-coded risk levels (High/Medium/Low)
- Pattern highlighting with visual feedback
- Company-centric analysis view

### 🚀 High Performance
- Optimized Cypher queries for Neo4j
- Graph Data Science (GDS) algorithms
- RESTful API with FastAPI
- Responsive web interface

### 📓 Jupyter Notebooks
- Step-by-step data generation
- Automated Neo4j ingestion
- Complete network fraud analysis
- Visualization and reporting

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   Fraud Detection System                      │
└──────────────────────────────────────────────────────────────┘

  📓 Jupyter Notebooks               🗄️ Neo4j Database
  ┌─────────────────┐               ┌─────────────────┐
  │ 1. Generate     │────────▶      │  Graph Database │
  │    Synthetic    │               │   - Companies   │
  │    Data         │               │   - Auditors    │
  └─────────────────┘               │   - Relations   │
                                    └─────────────────┘
  ┌─────────────────┐                       │
  │ 2. Ingest Data  │────────▶              │
  │    into Neo4j   │                       │
  └─────────────────┘                       │
                                            │
  ┌─────────────────┐                       │
  │ 3. Analyze      │◀────────▶             │
  │    Complete     │      Query            │
  │    Network      │                       │
  └─────────────────┘                       │
                                            │
                                            ▼
         ┌──────────────────────────────────────────┐
         │      fraud_detection_api/                │
         ├──────────────────────────────────────────┤
         │  FastAPI Backend (fraud_engine.py)       │
         │  • Pattern Detection Logic               │
         │  • Graph Algorithms                      │
         │  • Risk Scoring                          │
         └──────────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────────┐
         │  Web Interface (fraud_viewer.html)       │
         │  • Company Search                        │
         │  • Interactive Graph Visualization       │
         │  • Pattern Highlighting                  │
         │  • Real-time Risk Assessment             │
         └──────────────────────────────────────────┘
```

---

## 📸 Screenshots

### Main Interface - Network Visualization
![Network View](docs/images/network_visualization.png)
*Interactive graph showing company relationships with highlighted circular trade pattern*

### Pattern Detection Results
![Pattern Detection](docs/images/pattern_detection.png)
*Detailed view showing detected fraud patterns with risk scores*

### Simplified Network View
![Simple View](docs/images/simplified_view.png)
*Clean visualization with risk-level color coding*

### Analysis Panel
![Analysis Panel](docs/images/analysis_panel.png)
*Right panel showing detected patterns and risk metrics*

---

## 🚀 Installation

### Prerequisites

- **Python 3.8+**
- **Neo4j 5.x** with Graph Data Science (GDS) plugin
- **Jupyter Notebook** (for data generation/analysis)
- **Git**

### Step 1: Clone the Repository

```bash
git clone https://github.com/jhahimanshu3636/Fraud_detection.git
cd Fraud_detection
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install neo4j fastapi uvicorn faker jupyter pandas numpy
```

### Step 3: Set Up Neo4j Database

#### Option A: Docker (Recommended)

```bash
docker run -d \
    --name neo4j-fraud \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password123 \
    -e NEO4J_PLUGINS='["graph-data-science"]' \
    -e NEO4J_apoc_export_file_enabled=true \
    -e NEO4J_apoc_import_file_enabled=true \
    neo4j:5-enterprise
```

#### Option B: Neo4j Desktop

1. Download [Neo4j Desktop](https://neo4j.com/download/)
2. Create a new project
3. Add database with GDS plugin
4. Start the database
5. Note the connection URI (usually `bolt://localhost:7687`)

### Step 4: Configure Connection

Update Neo4j credentials in your files:

**For Notebooks:**
```python
# In notebooks
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password123"
```

**For API:**
```python
# In fraud_detection_api/fraud_engine.py
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password123"
```

### Step 5: Verify Installation

```bash
# Test Neo4j connection
python -c "from neo4j import GraphDatabase; print('✓ Neo4j driver installed')"

# Start Jupyter
jupyter notebook

# Test FastAPI
cd fraud_detection_api
uvicorn app:app --reload
# Visit http://localhost:8000/docs
```

---

## 📁 Project Structure

```
Fraud_detection/
│
├── 📓 notebooks/                          # Jupyter notebooks
│   ├── 1_data_generation.ipynb          # Generate synthetic fraud data
│   ├── 2_data_ingestion.ipynb           # Load data into Neo4j
│   └── 3_fraud_pattern_analysis.ipynb   # Analyze complete network
│
├── 📂 fraud_detection_api/               # FastAPI application
│   ├── app.py                           # FastAPI server & endpoints
│   ├── fraud_engine.py                  # Core fraud detection logic
│   └── fraud_viewer.html                # Interactive web interface
│
├── 📂 data/                              # Generated data files
│   ├── companies.json                   # Company data
│   ├── shareholders.json                # Shareholder data
│   ├── auditors.json                    # Auditor data
│   └── relationships.json               # Relationship data
│
├── 📂 docs/                              # Documentation
│   ├── images/                          # Screenshots
│   ├── API_REFERENCE.md                 # API documentation
│   └── PATTERNS.md                      # Fraud pattern details
│
├── 📄 README.md                          # This file
├── 📄 requirements.txt                   # Python dependencies
└── 📄 .gitignore                        # Git ignore rules
```

---

## 📚 Usage Guide

### Part 1: Data Generation (Notebooks)

The first notebook generates synthetic financial network data with embedded fraud patterns.

#### Running the Notebook

```bash
jupyter notebook notebooks/1_data_generation.ipynb
```

#### What It Does

1. **Generates Entities**:
   - 100 companies with realistic names and industries
   - 50 shareholders (individual and institutional)
   - 10 auditors with varying risk levels (HIGH/MEDIUM/LOW)
   - 500 invoices with amounts and dates

2. **Creates Relationships**:
   - `SUBSIDIARY_OF`: Company hierarchies
   - `OWNS_SHARE`: Ownership stakes (with percentage)
   - `AUDITED_BY`: Audit relationships
   - `SUPPLIES`: Supply chain (with annual volume)
   - `ISSUES_TO` & `PAYS`: Invoice relationships

3. **Embeds Fraud Patterns**:
   - **3-5 Shell Company Chains**: Subsidiaries sharing high-risk auditors
   - **4-6 Circular Trade Cycles**: Closed transaction loops
   - **5-8 Hidden Influence Cases**: Indirect control via suppliers

#### Output

```
✓ Generated 100 companies
✓ Generated 50 shareholders
✓ Generated 10 auditors
✓ Generated 500 invoices
✓ Embedded 3 shell company chains
✓ Embedded 5 circular trade cycles
✓ Embedded 6 hidden influence patterns
✓ Data saved to data/ directory
```

---

### Part 2: Data Ingestion to Neo4j

The second notebook loads the generated data into Neo4j database.

#### Running the Notebook

```bash
jupyter notebook notebooks/2_data_ingestion.ipynb
```

#### What It Does

1. **Connects to Neo4j**
   ```python
   driver = GraphDatabase.driver(
       "bolt://localhost:7687",
       auth=("neo4j", "password123")
   )
   ```

2. **Clears Existing Data** (if any)
   ```cypher
   MATCH (n) DETACH DELETE n
   ```

3. **Creates Constraints**
   ```cypher
   CREATE CONSTRAINT company_id IF NOT EXISTS 
   FOR (c:Company) REQUIRE c.company_id IS UNIQUE;
   ```

4. **Creates Indexes**
   ```cypher
   CREATE INDEX company_name IF NOT EXISTS 
   FOR (c:Company) ON (c.name);
   ```

5. **Loads All Entities**
   - Companies → `:Company` nodes
   - Shareholders → `:Shareholder` nodes
   - Auditors → `:Auditor` nodes
   - Invoices → `:Invoice` nodes

6. **Creates All Relationships**
   - With appropriate properties
   - Maintains referential integrity

#### Output

```
🗑️  Clearing existing data...
📋 Creating constraints and indexes...
🏢 Loading 100 companies... ✓
👤 Loading 50 shareholders... ✓
📋 Loading 10 auditors... ✓
🧾 Loading 500 invoices... ✓
🔗 Creating relationships...
   ├─ SUBSIDIARY_OF: 45 ✓
   ├─ OWNS_SHARE: 87 ✓
   ├─ AUDITED_BY: 100 ✓
   ├─ SUPPLIES: 234 ✓
   ├─ ISSUES_TO: 500 ✓
   └─ PAYS: 500 ✓
✅ Data ingestion complete!
```

#### Verification

Run these queries in Neo4j Browser (`http://localhost:7474`):

```cypher
// Check node counts
MATCH (c:Company) RETURN count(c) as companies;
MATCH (s:Shareholder) RETURN count(s) as shareholders;
MATCH (a:Auditor) RETURN count(a) as auditors;

// Visualize sample
MATCH (c:Company)-[r]->(n) 
RETURN c, r, n 
LIMIT 25;
```

---

### Part 3: Fraud Pattern Detection (Complete Network)

The third notebook analyzes the entire network for all three fraud patterns.

#### Running the Notebook

```bash
jupyter notebook notebooks/3_fraud_pattern_analysis.ipynb
```

#### What It Does

##### 1. Shell Company Chain Detection

**Algorithm**: Graph Traversal with Property Filtering

```cypher
MATCH (auditor:Auditor {risk_level: 'HIGH'})
MATCH (company:Company)-[:AUDITED_BY]->(auditor)
MATCH path=(company)-[:SUBSIDIARY_OF*3..10]->(root:Company)
WHERE ALL(n IN nodes(path) 
  WHERE exists((n)-[:AUDITED_BY]->(auditor)))
  AND ALL companies have <= 2 invoices
RETURN chain, chainLength, riskScore: 0.95
```

**Output**: List of all shell company chains with risk scores > 0.95

##### 2. Circular Trade Detection

**Algorithm**: Cycle Detection (Triangle Enumeration)

```cypher
MATCH (c1:Company)-[r1:SUPPLIES]->(c2:Company)
MATCH (c2)-[r2:SUPPLIES]->(c3:Company) 
MATCH (c3)-[r3:SUPPLIES]->(c1)
WHERE c1 <> c2 AND c2 <> c3 AND c1 <> c3
  AND r1.annual_volume >= 80
WITH [c1, c2, c3] AS cycle
RETURN cycle, totalVolume, isolationScore, riskScore
```

**Output**: All circular trade cycles with risk scores > 0.80

##### 3. Hidden Influence Detection

**Algorithm**: PageRank Centrality + Multi-hop Path Analysis

**Part A - PageRank**:
```cypher
CALL gds.graph.project(
  'ownership',
  ['Shareholder', 'Company'],
  {OWNS_SHARE: {properties: 'percentage'}}
)
CALL gds.pageRank.stream('ownership')
```

**Part B - Multi-hop Query**:
```cypher
MATCH (sh:Shareholder)-[owns:OWNS_SHARE]->(supplier:Company)
WHERE owns.percentage >= 25.0
MATCH (supplier)-[:SUPPLIES]->(target:Company)
WHERE concentration >= 80.0
  AND NOT exists((sh)-[:SUPPLIES]->(target))
RETURN sh, supplier, opportunityScore
```

**Output**: All hidden influence patterns with opportunity scores > 0.70

#### Analysis Results

The notebook generates comprehensive reports including:

- **Summary Statistics**:
  - Total patterns detected per type
  - Risk distribution histogram
  - Top 10 highest-risk companies

- **Visualizations**:
  - Network graphs with pattern highlighting
  - Risk heatmaps
  - Pattern distribution charts

- **Detailed Reports**:
  - CSV exports of all detected patterns
  - Company-wise risk breakdown
  - Relationship strength analysis

---

### Part 4: Fraud Detection API & UI

The `fraud_detection_api` directory contains the FastAPI backend and web interface for real-time, company-specific analysis.

#### Starting the API Server

```bash
cd fraud_detection_api
uvicorn app:app --reload --port 8000
```

Server will start at: `http://localhost:8000`

#### Opening the Web Interface

1. **Option A**: Direct file access
   ```bash
   # Open in browser
   open fraud_viewer.html
   # or
   firefox fraud_viewer.html
   ```

2. **Option B**: Using Python HTTP server
   ```bash
   python -m http.server 8080
   # Then navigate to http://localhost:8080/fraud_viewer.html
   ```

#### Using the Interface

##### 1. Company Search
```
┌─────────────────────────────────────────┐
│ 🔍 Fraud Detection    [c128    ] Analyze │
└─────────────────────────────────────────┘
```

- Enter company ID (e.g., `c128`, `c379`, `c497`)
- Press "Analyze" or hit Enter
- View results in ~1-2 seconds

##### 2. Interactive Graph Visualization

The main panel shows:
- **Blue node**: Queried company (enlarged)
- **Orange nodes**: Companies in circular trade
- **Gray nodes**: Other related entities
- **Green/Yellow/Red dots**: Risk levels (Low/Medium/High)
- **Arrows**: Relationships (SUPPLIES, OWNS_SHARE, etc.)

**Interactions**:
- 🖱️ **Pan**: Click and drag background
- 🔍 **Zoom**: Scroll wheel
- 👆 **Select Node**: Click any node
- 🖐️ **Drag Node**: Click and drag nodes

##### 3. Pattern Highlighting

**Left Panel - Highlight Patterns**:
```
┌─────────────────────┐
│ Highlight Patterns  │
├─────────────────────┤
│ ⛓️  Shell Chains     │
│ ✓  Circular Trade   │  ← Selected
│ 👤 Hidden Influence │
│ 🔄 Reset            │
└─────────────────────┘
```

Click any pattern to highlight:
- **Shell Chains**: Red highlighting
- **Circular Trade**: Orange highlighting with arrows
- **Hidden Influence**: Green highlighting

##### 4. Risk Levels Legend

```
┌─────────────────────────┐
│ Risk Levels             │
├─────────────────────────┤
│ 🔴 High (≥ 0.7)         │
│ 🟠 Medium (0.4-0.7)     │
│ 🟢 Low (< 0.4)          │
│ 🔵 Query Company        │
└─────────────────────────┘
```

##### 5. Detection Results Panel

**Right Panel - Detected Patterns**:

```
┌────────────────────────────────────┐
│ Detected Patterns                  │
├────────────────────────────────────┤
│ ⛓️ Shell Company Chains            │
│   No shell chains detected         │
│                                    │
│ 🔄 Circular Trade                  │
│   Cycle 1          Risk: 0.91      │
│   Volume: $363M                    │
│   Isolation: 75.0%                 │
│   C379 → C497 → C128              │
│                                    │
│ 👤 Hidden Influence                │
│   No hidden influence detected     │
└────────────────────────────────────┘
```

**Top Bar Metrics**:
```
Risk: 0.91    Entities: 89    Links: 113
```

#### Example Analysis Session

1. **Search for Company**:
   - Enter: `c128`
   - Click "Analyze"

2. **View Network**:
   - Graph loads showing c128 and connected entities
   - Blue node (c128) is centered and enlarged

3. **Highlight Pattern**:
   - Click "Circular Trade"
   - Orange arrows show: C379 → C497 → C128 → C379

4. **Check Details**:
   - Right panel shows:
     - Cycle 1 with Risk 0.91
     - Volume: $363M
     - Isolation: 75.0%
     - Path: C379 → C497 → C128

5. **Explore Further**:
   - Click on C379 node
   - Analyze that company
   - Discover more connections

---

## 🔍 Fraud Patterns Explained

### Pattern 1: Shell Company Chains 🔗

**What it detects**: Chains of subsidiary companies that share the same high-risk auditor and have unusually low business activity.

**Red Flags**:
- 3+ companies in a subsidiary chain
- All audited by same HIGH-risk auditor
- Each company has ≤2 invoices (very low activity)
- No legitimate business purpose evident

**Example**:
```
RootCo → SubCo1 → SubCo2 → SubCo3 → LeafCo
  ↓         ↓         ↓         ↓        ↓
  └─────────────────────────────────────┘
         All audited by "Risky Audit Inc"
         Each has 0-2 invoices per year
```

**Risk Score**: > 0.95 (Critical)

**Graph Theory Algorithm**: Graph Traversal with Property Filtering
- **Complexity**: O(V + E) where V=nodes, E=edges
- **Method**: Variable-length path matching in Cypher

---

### Pattern 2: Circular Trade 🔄

**What it detects**: Closed loops of high-volume transactions between companies with minimal external business.

**Red Flags**:
- 3+ companies form a closed cycle
- Each supplies to next in cycle
- High transaction volumes (>$80M annually)
- High isolation (few external connections)

**Example**:
```
     CompanyA ($90M)
         ↓
    CompanyB ($85M)
         ↓
    CompanyC ($92M)
         ↓
     CompanyA (closes loop)
```

**Isolation Score**:
```
isolation = cycle_size / (cycle_size + external_connections + 1)
```

**Risk Score**: 0.80 + (0.15 × isolation) = 0.80 to 0.95

**Graph Theory Algorithm**: Cycle Detection (Triangle Enumeration)
- **Complexity**: O(V³) worst case
- **Method**: Pattern matching for closed triangles

---

### Pattern 3: Hidden Influence 👤

**What it detects**: Shareholders who exert indirect control through concentrated supplier relationships.

**Red Flags**:
- Shareholder owns >25% of a supplier
- That supplier provides >80% of target's supplies
- Shareholder is NOT a direct supplier (hidden relationship)
- Shareholder has high PageRank (influential)

**Example**:
```
Influential Shareholder (PageRank: 0.85)
         ↓ owns 40%
    Supplier Company
         ↓ supplies 85% of invoices
    Target Company
```

**Opportunity Score**:
```
opportunity = 0.4 × PageRank 
            + 0.3 × (ownership / 50) 
            + 0.3 × (concentration / 100)
```

**Score**: > 0.70 (High opportunity for manipulation)

**Graph Theory Algorithm**: PageRank Centrality + Multi-hop Path Analysis
- **Complexity**: O(k × E) for PageRank where k=20 iterations
- **Method**: 2-hop pattern matching with centrality metrics

---

## 📡 API Reference

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Analyze Company
```http
GET /api/analyze/{company_id}
```

Analyzes a specific company for all fraud patterns.

**Parameters**:
- `company_id` (path, required): Company identifier (e.g., "c128")

**Example Request**:
```bash
curl http://localhost:8000/api/analyze/c128
```

**Example Response**:
```json
{
  "company_id": "c128",
  "company_name": "TechCorp Industries",
  "risk_score": 0.91,
  "opportunity_score": 0.0,
  "patterns": {
    "pattern1_shell": [],
    "pattern2_circular": [
      {
        "cycle": ["c379", "c497", "c128"],
        "cycleLength": 3,
        "totalVolume": 363.0,
        "avgVolume": 121.0,
        "externalConnections": 2,
        "isolationScore": 0.75,
        "riskScore": 0.91
      }
    ],
    "pattern3_hidden": []
  }
}
```

---

#### 2. Get Visualization Data
```http
GET /api/visualization/{company_id}
```

Returns graph data for network visualization.

**Parameters**:
- `company_id` (path, required): Company identifier

**Example Request**:
```bash
curl http://localhost:8000/api/visualization/c128
```

**Example Response**:
```json
{
  "nodes": [
    {
      "id": "c128",
      "label": "TechCorp Industries",
      "group": "company",
      "title": "Company: TechCorp Industries",
      "color": "#3b82f6",
      "size": 30
    },
    {
      "id": "c379",
      "label": "Supplier Corp",
      "group": "company",
      "title": "Company: Supplier Corp",
      "color": "#6b7280",
      "size": 20
    }
  ],
  "edges": [
    {
      "from": "c379",
      "to": "c497",
      "label": "SUPPLIES",
      "title": "Annual Volume: $121M",
      "width": 12.1,
      "arrows": "to"
    }
  ]
}
```

---

#### 3. List All Companies
```http
GET /api/companies
```

Returns list of all companies in the database.

**Query Parameters**:
- `limit` (optional, default=100): Maximum results
- `offset` (optional, default=0): Pagination offset

**Example Request**:
```bash
curl http://localhost:8000/api/companies?limit=10
```

**Example Response**:
```json
{
  "companies": [
    {
      "company_id": "c1",
      "name": "TechCorp Industries",
      "industry": "Technology"
    },
    {
      "company_id": "c2",
      "name": "Finance Solutions Ltd",
      "industry": "Finance"
    }
  ],
  "total": 100,
  "limit": 10,
  "offset": 0
}
```

---

#### 4. Health Check
```http
GET /health
```

Checks API and database connectivity.

**Example Request**:
```bash
curl http://localhost:8000/health
```

**Example Response**:
```json
{
  "status": "healthy",
  "api": "online",
  "neo4j": "connected",
  "database": {
    "companies": 100,
    "relationships": 1466
  },
  "timestamp": "2025-12-14T10:30:00Z"
}
```

---

### Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Explore all endpoints
- Test API calls directly in browser
- View request/response schemas
- Download OpenAPI specification

---

## 🛠️ Technologies Used

### Backend
- **[Python 3.8+](https://www.python.org/)** - Core programming language
- **[Neo4j 5.x](https://neo4j.com/)** - Graph database for network storage
- **[Neo4j GDS](https://neo4j.com/product/graph-data-science/)** - Graph algorithms (PageRank, etc.)
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[Uvicorn](https://www.uvicorn.org/)** - ASGI server

### Frontend
- **[Vis.js Network](https://visjs.org/)** - Graph visualization library
- **HTML5 + CSS3** - Modern web standards
- **Vanilla JavaScript** - No framework dependencies

### Data & Notebooks
- **[Jupyter](https://jupyter.org/)** - Interactive notebooks
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation
- **[NumPy](https://numpy.org/)** - Numerical computing
- **[Faker](https://faker.readthedocs.io/)** - Synthetic data generation

### Graph Algorithms
- **Graph Traversal** - Shell company detection
- **Cycle Detection** - Circular trade identification
- **PageRank** - Influence measurement
- **Multi-hop Path Analysis** - Hidden relationship discovery

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Neo4j Connection Failed

**Error**: `ServiceUnavailable: Unable to connect to Neo4j`

**Solutions**:
```bash
# Check if Neo4j is running
docker ps | grep neo4j
# or
systemctl status neo4j

# Verify credentials
NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="password123"

# Test connection
python -c "from neo4j import GraphDatabase; \
  driver = GraphDatabase.driver('bolt://localhost:7687', \
  auth=('neo4j', 'password123')); \
  driver.verify_connectivity(); \
  print('✓ Connected')"
```

---

#### 2. GDS Plugin Not Found

**Error**: `Unknown procedure: gds.pageRank`

**Solution**:
```bash
# For Docker
docker run -e NEO4J_PLUGINS='["graph-data-science"]' neo4j:5-enterprise

# For Neo4j Desktop
# Go to: Manage → Plugins → Install "Graph Data Science"

# Verify installation
# In Neo4j Browser:
CALL gds.version()
```

---

#### 3. CORS Errors in Browser

**Error**: `Access-Control-Allow-Origin header is missing`

**Solution**:
```python
# In fraud_detection_api/app.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

#### 4. Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000
# or
netstat -ano | grep 8000

# Kill the process
kill -9 <PID>

# Or use different port
uvicorn app:app --reload --port 8001
```

---

#### 5. Module Not Found

**Error**: `ModuleNotFoundError: No module named 'neo4j'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install neo4j fastapi uvicorn faker jupyter pandas
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Issues

1. Check existing [issues](https://github.com/jhahimanshu3636/Fraud_detection/issues)
2. Create new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)

### Suggesting Features

1. Open an issue with tag `enhancement`
2. Describe the feature and use case
3. Explain why it would be valuable

### Submitting Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/Fraud_detection.git
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes**
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   ```bash
   # Run notebooks
   # Test API endpoints
   # Check UI functionality
   ```

5. **Commit with clear message**
   ```bash
   git commit -m "feat: Add new fraud pattern detection"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Style

- **Python**: Follow PEP 8
- **JavaScript**: Use ES6+ features
- **Comments**: Explain "why", not "what"
- **Naming**: Use descriptive variable names

---

## 👥 Author

**Himanshu Jha**
- GitHub: [@jhahimanshu3636](https://github.com/jhahimanshu3636)
- LinkedIn: [Connect with me](https://linkedin.com/in/jhahimanshu3636)

---


---

## 📞 Support

Need help? Here's how to get support:

- **Documentation**: You're reading it! 📖
- **Issues**: [GitHub Issues](https://github.com/jhahimanshu3636/Fraud_detection/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jhahimanshu3636/Fraud_detection/discussions)
- **Email**: jhahimanshu3636@gmail.com

---

## ⭐ Star This Repository

If you find this project useful, please consider giving it a star! It helps others discover the project and motivates continued development.

[![GitHub stars](https://img.shields.io/github/stars/jhahimanshu3636/Fraud_detection?style=social)](https://github.com/jhahimanshu3636/Fraud_detection)

---

**Made with ❤️ using Graph Theory and FastAPI**