#!/bin/bash

# Test MCP stdio server manually
# This simulates what Claude Desktop does

echo "========================================="
echo "Testing MCP Stdio Server"
echo "========================================="
echo ""

# Check backend is running
echo "1. Checking backend server..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend server is running"
else
    echo "   ❌ Backend server is NOT running"
    echo "   Start it with: ./start_for_claude.sh"
    exit 1
fi

echo ""
echo "2. Testing MCP stdio wrapper..."
echo ""

# Test initialize
echo "   Testing 'initialize' method..."
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | venv/bin/python mcp_server.py 2>&1 | head -20

echo ""
echo "========================================="
echo "If you see a JSON response above, MCP server is working!"
echo "If you see errors, check them above."
echo "========================================="
