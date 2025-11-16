# Agnovat Analyst - MCP Integration Guide

**Deploy to Claude Desktop and other AI applications**

---

## Table of Contents

1. [What is MCP?](#what-is-mcp)
2. [Claude Desktop Integration](#claude-desktop-integration)
3. [Other AI Applications](#other-ai-applications)
4. [Testing MCP Connection](#testing-mcp-connection)
5. [Troubleshooting](#troubleshooting)

---

## What is MCP?

**Model Context Protocol (MCP)** is an open protocol that enables AI applications to access external tools and data sources. Agnovat Analyst implements MCP through FastAPI-MCP, making all 23 tools automatically available to any MCP-compatible AI application.

### How It Works

```
AI Application (Claude Desktop, etc.)
         ↓
    MCP Protocol
         ↓
  Agnovat Analyst Server (localhost:8000)
         ↓
    23 Analysis Tools
```

When connected via MCP:
- Claude can directly invoke any of the 23 tools
- No need for manual API calls or curl commands
- Tools appear as native functions in the AI interface
- Results are automatically formatted and returned

---

## Claude Desktop Integration

### Prerequisites

- **Claude Desktop** installed ([Download here](https://claude.ai/download))
- **Agnovat Analyst** server running
- **macOS, Windows, or Linux**

### Step 1: Locate Configuration File

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

### Step 2: Configure MCP Server

Edit the configuration file and add the Agnovat Analyst server:

```json
{
  "mcpServers": {
    "agnovat-analyst": {
      "command": "uvicorn",
      "args": [
        "app.main:app",
        "--host",
        "localhost",
        "--port",
        "8000"
      ],
      "cwd": "/Users/mandaza/Documents/Project/agnovat-docs",
      "env": {
        "PYTHONPATH": "/Users/mandaza/Documents/Project/agnovat-docs",
        "DEBUG": "False",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Important:** Update the `cwd` path to match your actual installation directory.

### Step 3: Using Virtual Environment (Recommended)

If you're using a virtual environment, use this configuration instead:

```json
{
  "mcpServers": {
    "agnovat-analyst": {
      "command": "/Users/mandaza/Documents/Project/agnovat-docs/venv/bin/uvicorn",
      "args": [
        "app.main:app",
        "--host",
        "localhost",
        "--port",
        "8000"
      ],
      "cwd": "/Users/mandaza/Documents/Project/agnovat-docs",
      "env": {
        "PYTHONPATH": "/Users/mandaza/Documents/Project/agnovat-docs",
        "DEBUG": "False",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Step 4: Restart Claude Desktop

1. **Quit Claude Desktop completely** (not just close the window)
2. **Restart Claude Desktop**
3. Claude will automatically connect to the MCP server on startup

### Step 5: Verify Connection

In Claude Desktop, you should see:
- A notification that "agnovat-analyst" MCP server is connected
- All 23 tools available in the tools menu

### Step 6: Using the Tools

Simply ask Claude to use the tools naturally:

**Examples:**

```
You: "Analyze this practitioner report for bias: /path/to/report.pdf"
Claude: [Automatically uses Tool 5: analyze_racism_bias]

You: "Extract family support evidence from this document: /path/to/report.pdf"
Claude: [Automatically uses Tool 10: extract_family_support]

You: "Generate a complete QCAT bundle for case GAA123/2024 using these documents..."
Claude: [Automatically uses Tool 23: generate_qcat_bundle]
```

---

## Other AI Applications

### Cline (VSCode Extension)

**Cline** is an AI coding assistant for VSCode that supports MCP.

**Configuration:**

1. Open VSCode settings
2. Search for "Cline MCP"
3. Add MCP server configuration:

```json
{
  "cline.mcpServers": {
    "agnovat-analyst": {
      "url": "http://localhost:8000",
      "type": "http"
    }
  }
}
```

### Continue.dev

**Continue** is another AI coding assistant with MCP support.

**Configuration (.continue/config.json):**

```json
{
  "mcpServers": [
    {
      "name": "agnovat-analyst",
      "url": "http://localhost:8000",
      "tools": ["all"]
    }
  ]
}
```

### OpenAI Custom GPTs

While OpenAI GPTs don't support MCP directly, you can expose Agnovat Analyst via API:

1. **Deploy with public endpoint** (see DEPLOYMENT.md for Nginx/HTTPS setup)
2. **Create OpenAPI spec** for GPT Actions
3. **Configure authentication**

**Quick OpenAPI export:**

```bash
curl http://localhost:8000/openapi.json > agnovat_openapi.json
```

Then import this into your Custom GPT's Actions configuration.

### LangChain Integration

Use Agnovat Analyst as a LangChain tool:

```python
from langchain.tools import Tool
import requests

def call_agnovat_tool(endpoint: str, payload: dict) -> dict:
    response = requests.post(f"http://localhost:8000/api/{endpoint}", json=payload)
    return response.json()

bias_tool = Tool(
    name="analyze_bias",
    func=lambda file_path: call_agnovat_tool(
        "analysis/analyze-racism-bias",
        {"file_path": file_path}
    ),
    description="Analyze practitioner reports for bias and racism"
)

# Add to your LangChain agent
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(temperature=0)
tools = [bias_tool]  # Add more tools as needed
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
```

### AutoGen Integration

Use with Microsoft AutoGen:

```python
from autogen import AssistantAgent, UserProxyAgent
import requests

def agnovat_function(tool_name: str, **kwargs):
    """Call Agnovat Analyst tools"""
    endpoint_map = {
        "analyze_bias": "analysis/analyze-racism-bias",
        "extract_family": "analysis/extract-family-support",
        "generate_bundle": "reports/qcat-bundle"
    }

    endpoint = endpoint_map.get(tool_name)
    response = requests.post(f"http://localhost:8000/api/{endpoint}", json=kwargs)
    return response.json()

# Configure agent with function
assistant = AssistantAgent(
    name="analyst",
    llm_config={
        "functions": [
            {
                "name": "analyze_bias",
                "description": "Analyze document for bias",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string"}
                    }
                }
            }
        ]
    }
)
```

---

## Testing MCP Connection

### 1. Check Server Status

```bash
curl http://localhost:8000/health
```

Expected:
```json
{
  "status": "healthy",
  "service": "agnovat-analyst",
  "version": "1.0.0"
}
```

### 2. Verify MCP Endpoint

```bash
curl http://localhost:8000/mcp/tools
```

Should list all 23 tools available via MCP.

### 3. Test Tool Invocation

From Claude Desktop or another MCP client, try:

```
"List all available Agnovat tools"
```

Claude should respond with all 23 tools.

### 4. Test Actual Analysis

```
"Use the health check to verify the Agnovat server is running"
```

Claude should invoke the health endpoint and report status.

---

## Troubleshooting

### Issue 1: Claude Desktop Can't Connect

**Symptoms:** "agnovat-analyst server failed to connect"

**Solutions:**

1. **Check server is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Verify configuration path:**
   - Ensure `cwd` points to correct directory
   - Use absolute paths, not relative

3. **Check Python environment:**
   ```bash
   which uvicorn  # Should point to venv if using venv
   ```

4. **Restart both:**
   ```bash
   # Stop server (Ctrl+C)
   # Quit Claude Desktop completely
   # Start server again
   uvicorn app.main:app --reload
   # Start Claude Desktop
   ```

### Issue 2: Tools Not Appearing

**Symptoms:** Server connected but tools don't show

**Solutions:**

1. **Check FastAPI-MCP version:**
   ```bash
   pip list | grep fastapi-mcp
   # Should be >= 0.1.0
   ```

2. **Verify endpoints:**
   ```bash
   curl http://localhost:8000/docs
   # Check all endpoints are listed
   ```

3. **Check logs:**
   ```bash
   # Server logs should show MCP tool registration
   ```

### Issue 3: Permission Denied

**Symptoms:** "Permission denied" when accessing files

**Solutions:**

1. **Use absolute paths:**
   ```
   /Users/mandaza/Documents/reports/report.pdf  # ✅ Good
   ./report.pdf  # ❌ May fail
   ```

2. **Check file permissions:**
   ```bash
   ls -la /path/to/file.pdf
   # Should be readable by user running server
   ```

### Issue 4: Port Already in Use

**Symptoms:** "Address already in use: 8000"

**Solutions:**

1. **Find process using port:**
   ```bash
   lsof -i :8000
   ```

2. **Kill existing process:**
   ```bash
   kill -9 <PID>
   ```

3. **Or use different port:**
   Update config to use port 8001, 8002, etc.

### Issue 5: Server Crashes on Tool Use

**Symptoms:** Server stops when Claude invokes a tool

**Solutions:**

1. **Check dependencies:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Check error logs:**
   Server console will show the error

3. **Verify PDF files exist:**
   Ensure file paths are valid

---

## Advanced Configuration

### Running Multiple Instances

To run multiple MCP servers:

```json
{
  "mcpServers": {
    "agnovat-analyst-prod": {
      "command": "uvicorn",
      "args": ["app.main:app", "--port", "8000"],
      "cwd": "/path/to/prod"
    },
    "agnovat-analyst-dev": {
      "command": "uvicorn",
      "args": ["app.main:app", "--port", "8001"],
      "cwd": "/path/to/dev"
    }
  }
}
```

### Environment Variables

Customize behavior with environment variables:

```json
{
  "mcpServers": {
    "agnovat-analyst": {
      "env": {
        "DEBUG": "False",
        "LOG_LEVEL": "WARNING",
        "BIAS_DETECTION_THRESHOLD": "0.7",
        "TEMPLATE_SIMILARITY_THRESHOLD": "0.85"
      }
    }
  }
}
```

### Auto-Start on Boot

**macOS (launchd):**

Create `~/Library/LaunchAgents/com.agnovat.analyst.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.agnovat.analyst</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/mandaza/Documents/Project/agnovat-docs/venv/bin/uvicorn</string>
        <string>app.main:app</string>
        <string>--host</string>
        <string>localhost</string>
        <string>--port</string>
        <string>8000</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/mandaza/Documents/Project/agnovat-docs</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load with:
```bash
launchctl load ~/Library/LaunchAgents/com.agnovat.analyst.plist
```

**Linux (systemd):** See DEPLOYMENT.md

---

## Security Considerations

### Local Development

When running locally:
- ✅ Server binds to localhost only (not accessible externally)
- ✅ No authentication needed
- ✅ Safe for personal use

### Production Deployment

If exposing to network:
- 🔐 Use HTTPS (see DEPLOYMENT.md for Nginx setup)
- 🔐 Implement API key authentication
- 🔐 Use firewall rules
- 🔐 Restrict file access paths
- 🔐 Enable rate limiting

---

## Best Practices

### 1. Keep Server Running

For best experience with Claude Desktop:
- Keep server running in background
- Use systemd/launchd for auto-start
- Monitor health endpoint

### 2. Use Absolute Paths

Always use absolute paths for files:
```
✅ /Users/mandaza/Documents/reports/report.pdf
❌ ./report.pdf
❌ ~/Documents/reports/report.pdf
```

### 3. Monitor Logs

Keep server logs visible to catch issues:
```bash
uvicorn app.main:app --reload --log-level info
```

### 4. Update Regularly

Keep dependencies updated:
```bash
pip install -r requirements.txt --upgrade
```

---

## Example Workflows

### Workflow 1: Quick Bias Check

**In Claude Desktop:**
```
You: "Check this report for bias: /path/to/report.pdf"

Claude: [Uses analyze_racism_bias tool]
"I found 12 instances of bias across 6 categories:
- Explicit racism: 2 instances
- Implicit bias: 5 instances
- Stigmatizing language: 5 instances
Overall risk score: 7/10"
```

### Workflow 2: Complete QCAT Analysis

**In Claude Desktop:**
```
You: "Generate a complete QCAT bundle for my case. Client name is John Smith,
case number GAA123/2024. Analyze these documents:
- /path/to/report1.pdf
- /path/to/report2.pdf
- /path/to/ndis_plan.pdf"

Claude: [Uses multiple tools automatically]
"I've generated your QCAT bundle including:
1. Guardianship argument report
2. Evidence summary
3. Document register with SHA-256 hashes
4. Timeline analysis
5. Contradiction matrix
6. NDIS goals alignment analysis

The bundle shows strong evidence for family guardianship..."
```

### Workflow 3: Comparative Analysis

**In Claude Desktop:**
```
You: "Compare these two versions of the practitioner report and identify
contradictions: /path/to/v1.pdf and /path/to/v2.pdf"

Claude: [Uses compare_documents and contradiction_matrix tools]
"I found 8 contradictions between the reports:
1. Risk assessment changed from 'moderate' to 'high' with no new evidence
2. Family involvement description differs significantly
..."
```

---

## Support and Resources

- **API Documentation:** http://localhost:8000/docs
- **User Guide:** [USER_GUIDE.md](USER_GUIDE.md)
- **Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **MCP Protocol:** https://modelcontextprotocol.io

---

**Ready to use Agnovat Analyst with Claude Desktop and other AI apps!** 🚀

For issues or questions, check the troubleshooting section above or consult the API documentation.
