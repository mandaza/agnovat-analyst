# Agnovat Analyst MCP Server

**AI-Powered Analysis System for QCAT Guardianship Appeals**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)]()

---

## 🎯 Overview

Agnovat Analyst is a comprehensive **Model Context Protocol (MCP)** server that provides **23 specialized AI tools** for analyzing practitioner reports in Queensland Civil and Administrative Tribunal (QCAT) guardianship cases. It helps identify bias, extract evidence, ensure legal compliance, and generate tribunal-ready documentation.

### ✨ Key Features

- **🔍 Bias Detection** - 6 categories analyzing racism, discrimination, and stigmatizing language with 38+ detection patterns
- **📊 Evidence Extraction** - Automated identification of family support capacity and Public Guardian limitations
- **⚖️ Legal Framework Analysis** - Compliance checking against Guardianship Act 2000 & Human Rights Act 2019 (Qld)
- **🎯 NDIS Goals Alignment** - Critical analysis tool demonstrating which guardianship option best supports client outcomes (G1-G7)
- **📝 QCAT-Ready Reports** - Automated generation of evidence bundles, legal arguments, and contradiction matrices
- **🔐 Document Integrity** - SHA-256 hashing and chain of custody verification
- **🤖 AI Integration** - Works with Claude Desktop, Cline, Continue.dev, LangChain, and any MCP-compatible application

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/agnovat-docs.git
cd agnovat-docs

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# Create environment file
cp .env.example .env
```

### Running the Server

```bash
# Start the FastAPI server
uvicorn app.main:app --reload

# Test the server
curl http://localhost:8000/health
```

**API Documentation:** http://localhost:8000/docs

📖 **[Complete Installation Guide →](docs/QUICK_START.md)**

---

## 🔌 Claude Desktop Integration

Use all 23 tools directly in Claude Desktop with MCP!

### Quick Setup

```bash
# 1. Start the backend server (if not already running)
./start_for_claude.sh

# 2. Copy MCP configuration
# macOS
cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
cp claude_desktop_config.json ~/.config/Claude/claude_desktop_config.json

# Windows
copy claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json

# 3. Restart Claude Desktop
```

### Using in Claude

```
"List all available Agnovat tools"

"Analyze this practitioner report for bias: /path/to/report.pdf"

"Extract family support evidence from: /path/to/document.pdf"

"Generate a complete QCAT bundle for case GAA123/2024 using:
- /path/to/report1.pdf
- /path/to/report2.pdf
- /path/to/ndis_plan.pdf"
```

📘 **[Complete MCP Integration Guide →](docs/MCP_INTEGRATION.md)**
📋 **[Claude Desktop Setup Guide →](CLAUDE_DESKTOP_SETUP.md)**

---

## 📚 All 23 Tools

| # | Tool Name | Category | Description |
|---|-----------|----------|-------------|
| 1-4 | **PDF Processing** | Document Handling | Text extraction, hashing, integrity verification, metadata |
| 5 | **Bias & Racism Analysis** ⭐ | Bias Detection | Detects 6 categories: explicit racism, implicit bias, stigma, etc. |
| 6-9 | **Document Analysis** | Quality Control | Inconsistencies, template reuse, omissions, non-evidence statements |
| 10-11 | **Evidence Extraction** | Case Building | Family support capacity (6 themes), PG limitations |
| 12-15 | **Comparison & Timeline** | Analysis | Document comparison, timeline extraction, contradiction matrices |
| 16-19 | **Legal Framework** | Compliance | Human rights breaches, risk assessment, bias detection, language compliance |
| 20 | **NDIS Goals Alignment** ⭐⭐⭐ | Critical Analysis | Analyzes G1-G7 goals for family vs PG guardianship fit |
| 21-23 | **Report Generation** | Output | Guardianship arguments, evidence summaries, complete QCAT bundles |

**Status:** 🎉 **100% Complete** - All 23 tools implemented and operational!

---

## 💡 Use Cases

### 1. Challenge Biased Assessments
- Detect racism, implicit bias, and stigmatizing language
- Identify human rights breaches (HR Act 2019 Qld)
- Check professional language compliance

### 2. Demonstrate Family Capacity
- Extract 6 themes of family support evidence
- Build timeline of sustained involvement
- Prove NDIS goals better served by family guardianship

### 3. Identify Report Weaknesses
- Find template reuse and copy-paste patterns
- Detect omitted context and non-evidence statements
- Generate contradiction matrices across documents

### 4. Generate QCAT Submissions
- Automated legal argument generation
- Evidence summaries with chain of custody
- Complete tribunal-ready documentation bundles

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                 AI Applications                      │
│  (Claude Desktop, Cline, LangChain, etc.)           │
└──────────────────┬──────────────────────────────────┘
                   │ MCP Protocol
┌──────────────────▼──────────────────────────────────┐
│            MCP Server (stdio wrapper)               │
│              mcp_server.py                          │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP
┌──────────────────▼──────────────────────────────────┐
│         FastAPI Backend (port 8000)                 │
│                                                     │
│  ┌─────────────────────────────────────────┐      │
│  │  23 Analysis Tools                      │      │
│  │  - PDF Processing                       │      │
│  │  - Bias Detection (BiasDetector)        │      │
│  │  - Document Analysis                    │      │
│  │  - Evidence Extraction                  │      │
│  │  - Legal Framework                      │      │
│  │  - NDIS Goals Analyzer                  │      │
│  │  - Report Generation                    │      │
│  └─────────────────────────────────────────┘      │
│                                                     │
│  ┌─────────────────────────────────────────┐      │
│  │  NLP Services                           │      │
│  │  - spaCy (en_core_web_sm)              │      │
│  │  - Pattern matching                     │      │
│  │  - Sentiment analysis                   │      │
│  └─────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────┘
```

---

## 📖 Documentation

| Guide | Description | Link |
|-------|-------------|------|
| 🚀 Quick Start | Get running in 5 minutes | [QUICK_START.md](docs/QUICK_START.md) |
| 🔌 MCP Integration | Claude Desktop & AI apps setup | [MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md) |
| 📘 User Guide | Complete usage documentation | [USER_GUIDE.md](docs/USER_GUIDE.md) |
| 🚢 Deployment | Production deployment guide | [DEPLOYMENT.md](docs/DEPLOYMENT.md) |
| 🖥️ Claude Desktop | Detailed Claude Desktop setup | [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md) |

---

## 🧪 Testing

```bash
# Run comprehensive test suite
python tests/test_all_tools.py

# Test MCP connection
python test_mcp_connection.py

# Test stdio communication
./test_mcp_stdio.sh
```

---

## 🛠️ Development

### Project Structure

```
agnovat-docs/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic (23 tools)
│   └── tools/               # API endpoints
├── docs/                    # Documentation
├── configs/                 # Integration configs
├── tests/                   # Test suite
├── mcp_server.py           # MCP stdio wrapper
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Tech Stack

- **FastAPI** - Modern web framework for APIs
- **FastAPI-MCP** - MCP protocol integration
- **spaCy** - Natural language processing
- **PyPDF2 & pdfplumber** - PDF text extraction
- **Pydantic v2** - Data validation
- **httpx** - Async HTTP client
- **loguru** - Logging

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/agnovat-docs.git
cd agnovat-docs

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies including dev tools
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black app/ tests/
```

---

## ⚖️ Legal & Ethical Use

**Important:** This tool is designed for legitimate QCAT guardianship appeals where:
- There is genuine concern about bias or discrimination in practitioner reports
- Families are advocating for the best interests of their loved ones
- Evidence-based analysis supports family guardianship arrangements

**Not for:**
- Frivolous or vexatious litigation
- Manipulating evidence
- Undermining legitimate safeguarding concerns

Always consult with qualified legal professionals when preparing tribunal submissions.

---

## 📋 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Queensland Civil and Administrative Tribunal (QCAT)
- NDIS (National Disability Insurance Scheme)
- Guardianship Act 2000 (Qld)
- Human Rights Act 2019 (Qld)
- Model Context Protocol (MCP) by Anthropic

---

## 📞 Support

- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/yourusername/agnovat-docs/issues)
- **MCP Protocol:** https://modelcontextprotocol.io

---

## ⭐ Star History

If you find this project helpful, please consider giving it a star on GitHub!

---

**Built with ❤️ for families advocating for their loved ones in QCAT guardianship proceedings**
