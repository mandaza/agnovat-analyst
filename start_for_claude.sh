#!/bin/bash

# Agnovat Analyst - Startup Script for Claude Desktop Integration
# This script starts the FastAPI backend server that the MCP wrapper needs

set -e

echo "========================================="
echo "Agnovat Analyst - Claude Desktop Setup"
echo "========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📍 Working directory: $SCRIPT_DIR"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create it first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

echo "✅ Virtual environment found"
echo ""

# Check if server is already running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Server is already running on port 8000"
    echo ""
    read -p "Kill existing server and restart? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Killing existing server..."
        pkill -f "uvicorn app.main:app" || true
        sleep 2
    else
        echo "Keeping existing server running."
        echo ""
        echo "✅ Backend server is ready!"
        echo "✅ Claude Desktop can now connect via MCP"
        echo ""
        echo "Next steps:"
        echo "1. Copy config: cp claude_desktop_config.json ~/Library/Application\\ Support/Claude/"
        echo "2. Restart Claude Desktop"
        echo "3. You should see 'agnovat-analyst' connected"
        exit 0
    fi
fi

echo "🚀 Starting Agnovat Analyst backend server..."
echo ""
echo "The server will run in the background."
echo "Logs will be written to: server.log"
echo ""

# Start server in background
nohup venv/bin/uvicorn app.main:app --host localhost --port 8000 > server.log 2>&1 &
SERVER_PID=$!

echo "Server PID: $SERVER_PID"
echo "Waiting for server to start..."
sleep 3

# Check if server started successfully
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo ""
    echo "========================================="
    echo "✅ Backend Server Started Successfully!"
    echo "========================================="
    echo ""
    echo "Server is running at: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo "Logs: $SCRIPT_DIR/server.log"
    echo "PID: $SERVER_PID"
    echo ""
    echo "========================================="
    echo "Now Configure Claude Desktop"
    echo "========================================="
    echo ""
    echo "Run this command to copy the config:"
    echo "  cp claude_desktop_config.json ~/Library/Application\\ Support/Claude/claude_desktop_config.json"
    echo ""
    echo "Then:"
    echo "1. Quit Claude Desktop completely (Cmd+Q)"
    echo "2. Restart Claude Desktop"
    echo "3. You should see 'agnovat-analyst' server connected"
    echo "4. Try: 'List all available Agnovat tools'"
    echo ""
    echo "To stop the server:"
    echo "  kill $SERVER_PID"
    echo "  # or: pkill -f 'uvicorn app.main:app'"
    echo ""
else
    echo ""
    echo "❌ Server failed to start!"
    echo "Check logs: tail -f server.log"
    exit 1
fi
