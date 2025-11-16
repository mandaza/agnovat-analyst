#!/bin/bash

# Agnovat Analyst - Docker Deployment Script
# Deploys the backend to Docker and configures MCP for Claude Desktop

set -e

echo "========================================="
echo "Agnovat Analyst - Docker Deployment"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}❌ Docker is not installed!${NC}"
    echo "Please install Docker from: https://www.docker.com/get-started"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  docker-compose not found, using 'docker compose' instead${NC}"
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo -e "${BLUE}🐳 Step 1: Building Docker image...${NC}"
$DOCKER_COMPOSE build

echo ""
echo -e "${BLUE}🚀 Step 2: Starting containers...${NC}"
$DOCKER_COMPOSE up -d

echo ""
echo -e "${BLUE}⏳ Step 3: Waiting for server to start...${NC}"
sleep 5

# Check if server is healthy
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend server is running in Docker!${NC}"
    echo ""
    echo "Server details:"
    echo "  Container: agnovat-analyst"
    echo "  URL: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
else
    echo -e "${YELLOW}❌ Server failed to start. Checking logs...${NC}"
    $DOCKER_COMPOSE logs --tail=50
    exit 1
fi

echo ""
echo -e "${BLUE}🔌 Step 4: Configuring MCP for Claude Desktop...${NC}"

# Update MCP server to connect to Docker backend
cat > mcp_server_docker.py << 'MCP_EOF'
#!/usr/bin/env python3
"""
MCP Server for Claude Desktop - Docker Backend Version
Connects to Agnovat backend running in Docker
"""

import sys
import json
import asyncio
from typing import Any, Dict
import httpx
from loguru import logger

# Configure logger to stderr only
logger.remove()
logger.add(sys.stderr, level="INFO")

# Docker backend URL
BACKEND_URL = "http://localhost:8000"

# Import the MCP server class
import os
sys.path.insert(0, os.path.dirname(__file__))

from mcp_server import MCPStdioServer

# Override base_url to point to Docker
class MCPDockerServer(MCPStdioServer):
    def __init__(self):
        super().__init__(base_url=BACKEND_URL)

async def main():
    """Start MCP server connected to Docker backend"""
    logger.info("Starting MCP server (Docker backend mode)")
    server = MCPDockerServer()
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
MCP_EOF

chmod +x mcp_server_docker.py

# Create Docker-specific Claude Desktop config
cat > claude_desktop_config_docker.json << 'CONFIG_EOF'
{
  "mcpServers": {
    "agnovat-analyst": {
      "command": "VENV_PYTHON_PATH",
      "args": [
        "PROJECT_PATH/mcp_server_docker.py"
      ],
      "cwd": "PROJECT_PATH",
      "env": {
        "PYTHONPATH": "PROJECT_PATH"
      }
    }
  }
}
CONFIG_EOF

# Replace placeholders
VENV_PYTHON=$(which python3)
PROJECT_PATH=$(pwd)
sed -i.bak "s|VENV_PYTHON_PATH|$VENV_PYTHON|g" claude_desktop_config_docker.json
sed -i.bak "s|PROJECT_PATH|$PROJECT_PATH|g" claude_desktop_config_docker.json
rm -f claude_desktop_config_docker.json.bak

echo ""
echo -e "${GREEN}✅ MCP configuration created: claude_desktop_config_docker.json${NC}"

echo ""
echo "========================================="
echo -e "${GREEN}✅ Docker Deployment Complete!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Copy MCP config to Claude Desktop:"
echo "   # macOS"
echo "   cp claude_desktop_config_docker.json ~/Library/Application\\ Support/Claude/claude_desktop_config.json"
echo ""
echo "   # Linux"
echo "   cp claude_desktop_config_docker.json ~/.config/Claude/claude_desktop_config.json"
echo ""
echo "2. Restart Claude Desktop (Cmd+Q, then reopen)"
echo ""
echo "3. Test in Claude:"
echo '   "List all available Agnovat tools"'
echo ""
echo "Useful Docker commands:"
echo "  docker-compose logs -f          # View logs"
echo "  docker-compose ps               # Check status"
echo "  docker-compose stop             # Stop containers"
echo "  docker-compose restart          # Restart"
echo "  docker-compose down             # Stop and remove"
echo ""
