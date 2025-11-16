# Agnovat Analyst - Quick Start Guide

**Get up and running in 5 minutes!**

---

## Step 1: Install (2 minutes)

```bash
# Clone or navigate to project directory
cd agnovat-docs

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

---

## Step 2: Configure (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Edit if needed (defaults work for local development)
nano .env
```

Key settings:
```env
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

---

## Step 3: Start Server (30 seconds)

```bash
uvicorn app.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process
```

---

## Step 4: Test (1 minute)

### Health Check
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

### View API Docs
Open in browser: **http://localhost:8000/docs**

---

## Step 5: Run Your First Analysis (30 seconds)

Replace `/path/to/your/document.pdf` with actual PDF path:

```bash
curl -X POST "http://localhost:8000/api/analysis/analyze-racism-bias" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/your/document.pdf"
  }'
```

---

## Common First Tasks

### Analyze a Practitioner Report

```bash
# 1. Extract text
curl -X POST "http://localhost:8000/api/pdf/extract-text" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/report.pdf"}'

# 2. Detect bias
curl -X POST "http://localhost:8000/api/analysis/analyze-racism-bias" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/report.pdf"}'

# 3. Extract family evidence
curl -X POST "http://localhost:8000/api/analysis/extract-family-support" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/report.pdf"}'
```

### Analyze NDIS Goals Alignment ⭐ CRITICAL

```bash
curl -X POST "http://localhost:8000/api/legal/goals-guardianship-alignment" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/ndis_plan.pdf",
    "guardianship_context": "Family guardianship application"
  }'
```

### Generate Complete QCAT Report

```bash
curl -X POST "http://localhost:8000/api/reports/guardianship-argument" \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Client Name",
    "documents": ["/path/to/report1.pdf", "/path/to/report2.pdf"],
    "ndis_plan_path": "/path/to/ndis_plan.pdf",
    "include_goals_analysis": true,
    "include_human_rights": true
  }'
```

---

## Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Analyze bias
response = requests.post(
    f"{BASE_URL}/api/analysis/analyze-racism-bias",
    json={"file_path": "/path/to/report.pdf"}
)

result = response.json()
print(f"Flagged segments: {result['total_flagged_segments']}")
print(f"Risk score: {result['overall_risk_score']}/10")
```

---

## Interactive Exploration

Use the **Interactive API Documentation** at http://localhost:8000/docs

1. Click on any endpoint
2. Click "Try it out"
3. Fill in parameters
4. Click "Execute"
5. View results

---

## Next Steps

✅ **You're ready!** The system is running and operational.

**Continue learning:**
- 📖 [User Guide](USER_GUIDE.md) - Complete usage documentation
- 🔧 [API Reference](API_REFERENCE.md) - Detailed API docs
- 🧪 [Testing Guide](../TESTING_GUIDE.md) - Run test suite
- 🚀 [Deployment Guide](DEPLOYMENT.md) - Production deployment

**Common workflows:**
- Analyze single document for bias
- Compare multiple report versions
- Generate QCAT evidence bundle
- Run comprehensive analysis suite

---

## Troubleshooting

**Server won't start?**
```bash
# Check dependencies
pip list | grep fastapi

# Reinstall if needed
pip install -r requirements.txt --force-reinstall
```

**Can't access API docs?**
```bash
# Check DEBUG setting in .env
DEBUG=True  # Must be True for docs
```

**File not found errors?**
```bash
# Use absolute paths
/Users/yourname/Documents/report.pdf  # ✅ Good
./report.pdf  # ❌ May not work
```

---

## Quick Reference

| Task | Endpoint | Tool # |
|------|----------|--------|
| Detect bias | POST /api/analysis/analyze-racism-bias | 5 |
| Extract family evidence | POST /api/analysis/extract-family-support | 10 |
| NDIS goals alignment | POST /api/legal/goals-guardianship-alignment | 20 ⭐ |
| Generate QCAT report | POST /api/reports/guardianship-argument | 21 |
| Complete bundle | POST /api/reports/qcat-bundle | 23 |

---

**That's it! You're ready to start analyzing documents.** 🚀

For detailed documentation, see the [User Guide](USER_GUIDE.md).
