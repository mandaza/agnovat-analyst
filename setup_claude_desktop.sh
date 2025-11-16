#!/bin/bash

# Agnovat Analyst - Claude Desktop Setup Script
# This script automatically configures Claude Desktop to use Agnovat Analyst MCP Server

set -e

echo "========================================="
echo "Agnovat Analyst - Claude Desktop Setup"
echo "========================================="
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Windows;;
    MINGW*)     MACHINE=Windows;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "Detected OS: ${MACHINE}"
echo ""

# Set config path based on OS
if [ "$MACHINE" = "Mac" ]; then
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
elif [ "$MACHINE" = "Linux" ]; then
    CONFIG_DIR="$HOME/.config/Claude"
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
elif [ "$MACHINE" = "Windows" ]; then
    CONFIG_DIR="$APPDATA/Claude"
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
else
    echo "❌ Unsupported operating system: ${MACHINE}"
    exit 1
fi

echo "Claude Desktop config location: $CONFIG_FILE"
echo ""

# Check if Claude Desktop is installed
if [ ! -d "$CONFIG_DIR" ]; then
    echo "⚠️  Claude Desktop config directory not found."
    echo "Please install Claude Desktop from: https://claude.ai/download"
    echo ""
    read -p "Create config directory anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    mkdir -p "$CONFIG_DIR"
fi

# Get current directory (where Agnovat is installed)
AGNOVAT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Agnovat installation directory: $AGNOVAT_DIR"
echo ""

# Check if virtual environment exists
if [ -d "$AGNOVAT_DIR/venv" ]; then
    echo "✅ Found virtual environment"
    UVICORN_PATH="$AGNOVAT_DIR/venv/bin/uvicorn"
else
    echo "⚠️  Virtual environment not found. Using system uvicorn."
    UVICORN_PATH="uvicorn"
fi

# Create backup of existing config
if [ -f "$CONFIG_FILE" ]; then
    BACKUP_FILE="$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "📋 Backing up existing config to: $BACKUP_FILE"
    cp "$CONFIG_FILE" "$BACKUP_FILE"
    echo ""
fi

# Create new configuration
echo "📝 Creating Claude Desktop configuration..."
cat > "$CONFIG_FILE" <<EOF
{
  "mcpServers": {
    "agnovat-analyst": {
      "command": "$UVICORN_PATH",
      "args": [
        "app.main:app",
        "--host",
        "localhost",
        "--port",
        "8000"
      ],
      "cwd": "$AGNOVAT_DIR",
      "env": {
        "PYTHONPATH": "$AGNOVAT_DIR",
        "DEBUG": "False",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
EOF

echo "✅ Configuration created successfully!"
echo ""

# Check if server is running
echo "🔍 Checking if Agnovat server is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Server is already running"
else
    echo "⚠️  Server is not running"
    echo ""
    echo "To start the server manually:"
    echo "  cd $AGNOVAT_DIR"
    echo "  uvicorn app.main:app --reload"
    echo ""
    read -p "Start server now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$AGNOVAT_DIR"
        echo "Starting server in background..."
        nohup uvicorn app.main:app --host localhost --port 8000 > server.log 2>&1 &
        echo "Server PID: $!"
        echo "Logs: $AGNOVAT_DIR/server.log"
        sleep 2

        # Verify server started
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ Server started successfully!"
        else
            echo "❌ Server failed to start. Check logs: $AGNOVAT_DIR/server.log"
        fi
    fi
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Restart Claude Desktop (quit completely and reopen)"
echo "2. Claude will automatically connect to Agnovat Analyst"
echo "3. You should see 'agnovat-analyst' in the connected servers"
echo "4. All 23 tools will be available to Claude"
echo ""
echo "Test by asking Claude:"
echo '  "List all available Agnovat tools"'
echo '  "Analyze this report for bias: /path/to/report.pdf"'
echo ""
echo "Configuration file: $CONFIG_FILE"
echo "Documentation: $AGNOVAT_DIR/docs/MCP_INTEGRATION.md"
echo ""
echo "✨ Happy analyzing!"
