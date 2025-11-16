# Agnovat Analyst - Integration Configurations

This directory contains example configurations for integrating Agnovat Analyst with various AI applications and frameworks.

---

## Available Configurations

### 1. Claude Desktop (`../claude_desktop_config.json`)

**Location:** Project root (`claude_desktop_config.json`)

**Description:** MCP configuration for Claude Desktop application

**Setup:**
```bash
# Automated setup (recommended)
./setup_claude_desktop.sh

# Or manual setup:
# macOS
cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
cp claude_desktop_config.json ~/.config/Claude/claude_desktop_config.json

# Windows
copy claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json
```

**Verify:**
1. Restart Claude Desktop completely
2. Check for "agnovat-analyst" in connected servers
3. Ask Claude: "List all available Agnovat tools"

---

### 2. Cline (VSCode Extension) (`cline_config.json`)

**Description:** Configuration for Cline AI coding assistant in VSCode

**Setup:**
1. Install Cline extension in VSCode
2. Open VSCode settings (JSON)
3. Merge `cline_config.json` contents into your settings

**Or via Command Palette:**
1. `Cmd/Ctrl + Shift + P`
2. Search "Preferences: Open Settings (JSON)"
3. Add configuration

**Verify:**
- Cline should show "agnovat-analyst" as available MCP server
- All 23 tools should be accessible

---

### 3. Continue.dev (`continue_config.json`)

**Description:** Configuration for Continue AI coding assistant

**Setup:**
```bash
# macOS/Linux
cp continue_config.json ~/.continue/config.json

# Windows
copy continue_config.json %USERPROFILE%\.continue\config.json
```

**Note:** Update `apiKey` in config with your Anthropic API key

**Verify:**
- Restart Continue extension
- MCP server should appear in Continue's tools menu

---

### 4. LangChain (`langchain_integration.py`)

**Description:** Python integration for LangChain agents

**Setup:**
```bash
# Install LangChain
pip install langchain openai

# Use in your project
from configs.langchain_integration import create_qcat_agent

agent = create_qcat_agent()
result = agent.run("Analyze /path/to/report.pdf for bias")
```

**Examples in file:**
- Basic agent setup
- Specialized QCAT agent
- Chain of thought analysis
- Multi-document workflow
- Complete QCAT analysis workflow

**Test connection:**
```python
from configs.langchain_integration import test_agnovat_connection
test_agnovat_connection()
```

---

## General Prerequisites

All integrations require:

1. **Agnovat server running:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Server health check passing:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Correct file paths in configuration**
   - Use absolute paths
   - Update `cwd` to match your installation directory

---

## Configuration Options

### Environment Variables

Customize Agnovat behavior via environment variables in configs:

```json
{
  "env": {
    "DEBUG": "False",
    "LOG_LEVEL": "INFO",
    "BIAS_DETECTION_THRESHOLD": "0.6",
    "TEMPLATE_SIMILARITY_THRESHOLD": "0.8"
  }
}
```

**Available variables:**
- `DEBUG`: Enable/disable debug mode (True/False)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `BIAS_DETECTION_THRESHOLD`: Sensitivity for bias detection (0.0-1.0)
- `TEMPLATE_SIMILARITY_THRESHOLD`: Threshold for template reuse (0.0-1.0)

### Port Configuration

If port 8000 is in use, change to different port:

```json
{
  "args": [
    "app.main:app",
    "--host", "localhost",
    "--port", "8001"  // Changed from 8000
  ]
}
```

Update all references to `localhost:8000` to `localhost:8001`

---

## Troubleshooting

### Server Not Connecting

**Check server status:**
```bash
curl http://localhost:8000/health
```

**Check server logs:**
```bash
# Server should show MCP endpoint registrations
```

### Tools Not Appearing

**Verify FastAPI-MCP:**
```bash
pip list | grep fastapi-mcp
# Should show version >= 0.1.0
```

**Check API docs:**
```bash
open http://localhost:8000/docs
# All 23 endpoints should be listed
```

### Permission Errors

**Use absolute paths:**
```
✅ /Users/mandaza/Documents/reports/report.pdf
❌ ~/Documents/reports/report.pdf
❌ ./report.pdf
```

---

## Advanced Integrations

### OpenAI Custom GPTs

Export OpenAPI spec:
```bash
curl http://localhost:8000/openapi.json > agnovat_openapi.json
```

Import into GPT Actions configuration.

### AutoGen

See LangChain integration example - similar pattern applies.

### HTTP API Direct

Any application can use the REST API:
```bash
curl -X POST "http://localhost:8000/api/analysis/analyze-racism-bias" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/document.pdf"}'
```

---

## Testing Integrations

### 1. Basic Connection Test

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

### 2. MCP Tools List

In Claude Desktop or compatible client:
```
"List all available Agnovat tools"
```

Should show all 23 tools.

### 3. Sample Analysis

```
"Analyze this document for bias: /path/to/sample.pdf"
```

Should invoke Tool 5 and return analysis.

---

## Support

For integration issues:

1. **Check documentation:** `docs/MCP_INTEGRATION.md`
2. **Verify server:** `curl http://localhost:8000/health`
3. **Check logs:** Server console output
4. **Test endpoints:** `http://localhost:8000/docs`

---

## Example Workflows

### Claude Desktop Workflow

```
User: "I need to analyze these practitioner reports for my QCAT case:
- /path/to/report1.pdf
- /path/to/report2.pdf
- /path/to/ndis_plan.pdf

Generate a complete QCAT bundle for John Smith, case GAA123/2024"

Claude: [Automatically uses multiple Agnovat tools]
- Tool 5: Analyze bias in each report
- Tool 10: Extract family support evidence
- Tool 20: Analyze NDIS goals alignment
- Tool 23: Generate complete QCAT bundle

[Returns comprehensive analysis and bundle]
```

### LangChain Workflow

```python
from configs.langchain_integration import complete_qcat_workflow

result = complete_qcat_workflow(
    practitioner_reports=["/path/to/report1.pdf", "/path/to/report2.pdf"],
    ndis_plan_path="/path/to/ndis_plan.pdf",
    client_name="John Smith",
    case_number="GAA123/2024"
)

print(result['qcat_bundle'])
```

---

## Security Notes

**Local Development:**
- Configurations use `localhost` only (not accessible externally)
- No authentication required for local use
- Safe for personal document analysis

**Production Use:**
- See `docs/DEPLOYMENT.md` for HTTPS setup
- Implement API key authentication
- Use firewall rules
- Restrict file access paths

---

**All configurations ready to use!** 🚀

Choose the integration that fits your workflow and follow the setup instructions above.
