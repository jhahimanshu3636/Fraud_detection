# Web Interface Usage Guide

## 🚀 Quick Start (2 Steps)

### Step 1: Start the FastAPI Backend

```bash
# Navigate to your project directory
cd /path/to/your/project

# Start the FastAPI server
uvicorn app:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 2: Open the Web Interface

```bash
# Simply open the HTML file in your browser
open fraud_viewer.html

# OR double-click fraud_viewer.html
# OR drag it into your browser window
```

**That's it!** The interface will automatically connect to your FastAPI backend at `http://localhost:8000`

---

## 📖 How to Use

### 1. Enter Company ID
- Type a company ID in the search box (e.g., `c32`, `c45`, `c100`)
- The default is `c32` - you can start with that

### 2. Click "Analyze"
- Click the green "Analyze" button
- OR press Enter while in the input field

### 3. Wait for Results
- You'll see a loading spinner
- The backend will:
  - Query Neo4j database
  - Detect fraud patterns
  - Build the network graph
  - Return visualization data

### 4. Explore the Visualization
- **Pan**: Click and drag the background
- **Zoom**: Mouse wheel
- **Hover**: See detailed information in tooltips
- **Click nodes**: Select and focus

### 5. Highlight Patterns
Click the buttons on the left side of the graph:
- **🔗 Shell Chains**: Highlights subsidiary chain patterns
- **🔄 Circular Trade**: Highlights circular trading patterns
- **👁️ Hidden Influence**: Highlights hidden shareholder influence
- **↺ Reset View**: Return to normal view

### 6. Review Pattern Details
Check the right sidebar for:
- Detailed pattern information
- Risk scores
- Entity relationships
- Metrics and statistics

---

## 🎯 Example Workflow

### Analyzing Company c32

1. **Open** `fraud_viewer.html` in your browser
2. **Ensure** FastAPI is running at `http://localhost:8000`
3. **Type** `c32` in the search box
4. **Click** "Analyze"
5. **Wait** 2-5 seconds for results
6. **Review** the statistics at the top
7. **Examine** the network graph
8. **Click** "Shell Chains" to see if any exist
9. **Click** "Circular Trade" to check for cycles
10. **Click** "Hidden Influence" to see shareholder patterns
11. **Try** another company by typing a new ID

---

## ⚙️ Configuration

### Change API Endpoint

If your FastAPI is running on a different port or server:

1. Find the "API Endpoint" field in the header
2. Change from `http://localhost:8000` to your endpoint
3. For example: `http://localhost:5000` or `http://192.168.1.100:8000`

### Test Different Companies

Try these company IDs:
- `c32` - Default test company
- `c45` - Alternative company
- `c78` - Another option
- `c100` - Different company

To find all available companies, run in Neo4j:
```cypher
MATCH (c:Company) RETURN c.company_id LIMIT 20
```

---

## 🎨 What You'll See

### Top Section - Input & Configuration
- Company ID search box
- Analyze button
- API endpoint configuration

### Statistics Bar (after analysis)
5 cards showing:
- **Risk Score**: Overall fraud risk (0-1)
- **Opportunity Score**: Business opportunity (0-1)
- **Total Entities**: Number of nodes
- **Relationships**: Number of connections
- **High Risk Nodes**: Count of risky entities

### Main Network Graph
- **Center**: Large, interactive network visualization
- **Nodes**: Colored dots representing entities
  - 🔴 Red: High risk (≥0.7)
  - 🟠 Orange: Medium risk (0.4-0.7)
  - 🟢 Green: Low risk (<0.4)
  - 🔵 Blue: Query company
- **Edges**: Lines showing relationships
- **Controls**: Pattern highlighting buttons

### Right Sidebar
- **Legend**: Color meanings
- **Shell Chains**: List of detected patterns
- **Circular Trade**: Cycle details
- **Hidden Influence**: Shareholder patterns

---

## 🔧 Troubleshooting

### Problem: "Failed to analyze company"

**Solution 1: Check FastAPI is running**
```bash
# In terminal, you should see the uvicorn server running
# If not, start it:
uvicorn app:app --reload --port 8000
```

**Solution 2: Test API manually**
```bash
# Open browser to:
http://localhost:8000/docs

# Or test with curl:
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

**Solution 3: Check the correct port**
- Default is port 8000
- If using different port, update in the "API Endpoint" field

### Problem: "Network timeout" or "Connection refused"

**Check:**
1. FastAPI server is running
2. API endpoint is correct (check port number)
3. No firewall blocking localhost
4. Try: `http://127.0.0.1:8000` instead of `localhost`

### Problem: "No data displayed"

**Possible causes:**
1. Company ID doesn't exist
   - Try: `c32`, `c45`, `c100`
   - Check Neo4j: `MATCH (c:Company {company_id: 'c32'}) RETURN c`

2. Company has no connections
   - Normal - not all companies have connections
   - Try a different company ID

3. Neo4j not running
   - Start Neo4j: `systemctl start neo4j`
   - Check: `systemctl status neo4j`

### Problem: Blank screen or errors in browser

**Check browser console:**
1. Press F12 (Chrome/Firefox)
2. Go to "Console" tab
3. Look for error messages
4. Common fixes:
   - Check API endpoint URL
   - Ensure no CORS issues (FastAPI should handle this)
   - Try a different browser

### Problem: Pattern buttons don't highlight anything

**This is normal if:**
- No patterns detected for this company
- Check sidebar - it will say "No patterns detected"
- Try a company known to have patterns

---

## 🌐 Browser Compatibility

Works with:
- ✅ Chrome/Chromium (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Opera

**Note:** Must have JavaScript enabled

---

## 💡 Tips for Best Results

1. **Start with c32**: It's the default test company
2. **Wait for loading**: Large networks take 5-10 seconds
3. **Use pattern buttons**: They help focus on specific fraud types
4. **Check sidebar**: Detailed pattern information is there
5. **Try multiple companies**: Compare different networks
6. **Zoom and pan**: Explore large networks by zooming in

---

## 📊 Understanding the Colors

| Color | Risk Level | What it Means |
|-------|-----------|---------------|
| 🔴 Red | High (≥0.7) | Significant fraud indicators |
| 🟠 Orange | Medium (0.4-0.7) | Moderate risk signals |
| 🟢 Green | Low (<0.4) | Low risk, likely legitimate |
| 🔵 Blue | N/A | The company you're analyzing |

---

## 🚀 Advanced Usage

### Analyzing Multiple Companies

1. Analyze first company (e.g., `c32`)
2. Note the patterns and connections
3. Change the company ID (e.g., `c45`)
4. Click "Analyze" again
5. Compare the two networks

### Exporting Results

**Take a screenshot:**
- Windows: `Win + Shift + S`
- Mac: `Cmd + Shift + 4`
- Linux: `PrintScreen` or screenshot tool

**Save the page:**
- Right-click → "Save Page As"
- Choose "Web Page, Complete"

---

## 📞 Getting Help

### Quick Checks

1. ✅ FastAPI server running?
   ```bash
   curl http://localhost:8000/health
   ```

2. ✅ Company exists in Neo4j?
   ```bash
   echo "MATCH (c:Company {company_id: 'c32'}) RETURN c" | cypher-shell -u neo4j -p password
   ```

3. ✅ Browser console for errors?
   Press F12 → Console tab

### Common Solutions

| Issue | Solution |
|-------|----------|
| Can't connect | Start FastAPI: `uvicorn app:app --reload` |
| Wrong port | Update API Endpoint field |
| No data | Try different company ID |
| Slow loading | Normal for large networks (wait ~10s) |
| Patterns not highlighting | Company may not have that pattern |

---

## 🎉 Success Checklist

- [ ] FastAPI server is running
- [ ] Opened `fraud_viewer.html` in browser
- [ ] Entered a company ID
- [ ] Clicked "Analyze"
- [ ] Saw the network graph appear
- [ ] Statistics bar shows data
- [ ] Can pan and zoom the graph
- [ ] Pattern buttons work
- [ ] Sidebar shows pattern details

**If all checked, you're ready to analyze fraud patterns! 🎯**

---

## 📝 Quick Reference

### Keyboard Shortcuts
- `Enter` in search box → Analyze
- `F12` → Open browser console
- `Ctrl/Cmd + Plus` → Zoom in page
- `Ctrl/Cmd + Minus` → Zoom out page

### Mouse Controls
- `Drag background` → Pan network
- `Mouse wheel` → Zoom network
- `Hover node` → Show tooltip
- `Click node` → Select node

### Pattern Detection
- 🔗 **Shell Chains**: Long subsidiary chains with high-risk auditors
- 🔄 **Circular Trade**: Companies trading in circles
- 👁️ **Hidden Influence**: Undisclosed shareholder control

---

**Ready to detect fraud! Open `fraud_viewer.html` and start analyzing! 🔍**
