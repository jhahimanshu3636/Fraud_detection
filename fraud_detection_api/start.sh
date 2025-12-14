#!/bin/bash

# Fraud Detection System Startup Script
# This script starts the FastAPI backend and opens the web interface

echo "================================================"
echo "  Fraud Detection Network Visualization System  "
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 is not installed"
    exit 1
fi

# Check if required files exist
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found"
    echo "Please run this script from the directory containing the application files"
    exit 1
fi

if [ ! -f "fraud_viewer.html" ]; then
    echo "❌ Error: fraud_viewer.html not found"
    exit 1
fi

echo "✅ Files found"
echo ""

# Check if uvicorn is installed
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "📦 Installing uvicorn..."
    pip install uvicorn --break-system-packages
fi

# Check if fastapi is installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing fastapi..."
    pip install fastapi --break-system-packages
fi

# Check if networkx is installed
if ! python3 -c "import networkx" 2>/dev/null; then
    echo "📦 Installing networkx..."
    pip install networkx --break-system-packages
fi

# Check if neo4j is installed
if ! python3 -c "import neo4j" 2>/dev/null; then
    echo "📦 Installing neo4j driver..."
    pip install neo4j --break-system-packages
fi

echo ""
echo "✅ All dependencies installed"
echo ""

# Start FastAPI server in background
echo "🚀 Starting FastAPI server..."
uvicorn app:app --reload --port 8000 &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 3

# Check if server is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ FastAPI server is running on http://localhost:8000"
else
    echo "⚠️  Warning: Server may not be ready yet. Waiting a bit more..."
    sleep 3
fi

echo ""
echo "================================================"
echo "  System Ready!  "
echo "================================================"
echo ""
echo "📊 FastAPI Backend: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo "🌐 Opening Web Interface..."
echo ""

# Open the web interface in default browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open fraud_viewer.html
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open fraud_viewer.html 2>/dev/null || echo "Please open fraud_viewer.html manually"
else
    # Windows (Git Bash, WSL, etc)
    start fraud_viewer.html 2>/dev/null || echo "Please open fraud_viewer.html manually"
fi

echo ""
echo "================================================"
echo "  How to Use:  "
echo "================================================"
echo ""
echo "1. Enter a company ID (e.g., c32) in the web interface"
echo "2. Click 'Analyze' button"
echo "3. Explore the interactive network visualization"
echo "4. Use pattern buttons to highlight fraud patterns"
echo ""
echo "💡 Press Ctrl+C to stop the server and exit"
echo ""

# Wait for user to stop the server
trap "echo ''; echo '🛑 Stopping server...'; kill $SERVER_PID 2>/dev/null; echo '✅ Server stopped. Goodbye!'; exit 0" INT

wait $SERVER_PID
