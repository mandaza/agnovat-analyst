# Development Guide

## Quick Start

### 1. Environment Setup

```bash
# Clone and navigate
cd agnovat-analyst

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

### 3. Run Development Server

```bash
# Start server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python module
python -m app.main
```

### 4. Access API Documentation

Open http://localhost:8000/docs in your browser to see the interactive API documentation.

---

## Development Workflow

### Phase 1: Core Infrastructure ✅
- [x] Project structure
- [x] Configuration management
- [x] Data models
- [x] API endpoints skeleton
- [x] PDF processing service

### Phase 2: PDF Processing Tools (Current)
**Tools 1-4**

Implementation checklist:
- [x] extract_pdf_text - IMPLEMENTED
- [x] generate_document_hash - IMPLEMENTED
- [x] verify_document_integrity - IMPLEMENTED
- [x] extract_metadata_and_timestamps - IMPLEMENTED

### Phase 3: NLP Analysis Foundation
**Tool 5: Bias and Racism Detection**

Tasks:
1. Set up transformers pipeline for bias detection
2. Create pattern matching for cultural terms
3. Implement stigmatizing language detection
4. Build scoring algorithm
5. Create narrative report generator

### Phase 4: Document Analysis Suite
**Tools 6-9**

Tasks:
1. Inconsistency detection (cross-document)
2. Template reuse detection (text similarity)
3. Omitted context detection (gap analysis)
4. Non-evidence statement detection

### Phase 5: Evidence Extraction
**Tools 10-11**

Tasks:
1. Family support evidence extraction
2. Public Guardian limitations extraction

### Phase 6: Comparison & Timeline
**Tools 12-15**

Tasks:
1. Document comparison engine
2. Combined analysis pipeline
3. Timeline extraction
4. Contradiction matrix generation

### Phase 7: Legal Framework
**Tools 16-19**

Tasks:
1. Human rights breach mapping
2. Risk assessment comparison
3. State guardianship bias detection
4. Professional language compliance

### Phase 8: NDIS Goals Alignment
**Tool 20** ⭐ CRITICAL

Tasks:
1. Goal definition and parsing (G1-G7)
2. Evidence extraction per goal
3. Alignment scoring algorithm
4. Conflict detection
5. Narrative generation per goal
6. Overall summary generation

### Phase 9: Report Generation
**Tools 21-23**

Tasks:
1. Guardianship argument report
2. QCAT evidence summary
3. Complete bundle assembly

### Phase 10: Testing & Documentation
Tasks:
1. Unit tests for all tools
2. Integration tests
3. API documentation
4. User guide
5. Deployment guide

---

## Architecture

### Service Layer Pattern

```
Tools (API Layer)
    ↓
Services (Business Logic)
    ↓
Models (Data Validation)
```

### Adding a New Tool

1. **Define Models** (`app/models/`)
```python
# In appropriate model file
class MyToolRequest(BaseModel):
    field: str = Field(..., description="Description")

class MyToolResponse(BaseModel):
    result: str = Field(..., description="Result")
```

2. **Implement Service** (`app/services/`)
```python
# In appropriate service file
async def my_tool_service(request: MyToolRequest) -> MyToolResponse:
    # Implementation
    return MyToolResponse(result="...")
```

3. **Create Endpoint** (`app/tools/`)
```python
# In appropriate router file
@router.post("/my-tool", response_model=MyToolResponse)
async def my_tool(request: MyToolRequest):
    """Tool documentation"""
    try:
        result = await my_tool_service(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

4. **Add Tests** (`tests/`)
```python
# In appropriate test file
def test_my_tool():
    # Test implementation
    pass
```

---

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_pdf_tools.py

# With coverage
pytest --cov=app --cov-report=html

# Verbose mode
pytest -v
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── fixtures/                # Test data
│   └── sample.pdf
├── test_pdf_tools.py        # PDF tool tests
├── test_analysis_tools.py   # Analysis tests
├── test_legal_tools.py      # Legal framework tests
└── test_reports.py          # Report generation tests
```

---

## Code Quality

### Formatting

```bash
# Format code
black app/ tests/

# Check formatting
black --check app/ tests/
```

### Linting

```bash
# Run linter
ruff check app/ tests/

# Auto-fix issues
ruff check --fix app/ tests/
```

### Type Checking

```bash
# Run mypy
mypy app/
```

---

## NLP Models

### spaCy

```python
# Load model
import spacy
nlp = spacy.load("en_core_web_sm")

# Process text
doc = nlp(text)
```

### Transformers

```python
# Load model for bias detection
from transformers import pipeline

classifier = pipeline("text-classification",
                     model="bert-base-uncased")
```

---

## Debugging

### Enable Debug Mode

```bash
# In .env
DEBUG=True
LOG_LEVEL=DEBUG
```

### View Logs

```bash
# Application logs
tail -f logs/app.log

# Uvicorn logs
# Displayed in console when running with --reload
```

### Debug Endpoints

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use loguru for detailed logging
from loguru import logger
logger.debug("Debug message with {}", variable)
```

---

## Common Issues

### PDF Extraction Errors

**Issue**: Cannot extract text from PDF
**Solution**: Some PDFs are scanned images. Consider adding OCR support with pytesseract.

### Memory Issues

**Issue**: Out of memory with large PDFs
**Solution**: Adjust PDF_MAX_PAGES or process in chunks.

### Model Loading Errors

**Issue**: spaCy model not found
**Solution**: Run `python -m spacy download en_core_web_sm`

---

## Performance Optimization

### Async/Await

All service functions should be async:

```python
async def process_document(file_path: str):
    # Long-running operation
    pass
```

### Caching

Consider caching for frequently accessed documents:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_document_analysis(file_hash: str):
    pass
```

### Batch Processing

Process multiple documents in parallel:

```python
import asyncio

results = await asyncio.gather(
    process_doc(doc1),
    process_doc(doc2),
    process_doc(doc3)
)
```

---

## Deployment

### Production Checklist

- [ ] Set DEBUG=False
- [ ] Configure secure SECRET_KEY
- [ ] Enable API_KEY_ENABLED
- [ ] Configure CORS appropriately
- [ ] Set up proper logging
- [ ] Configure file upload limits
- [ ] Set up backup for uploaded files
- [ ] Document retention policy
- [ ] Security audit
- [ ] Performance testing

### Docker Deployment

```dockerfile
# TODO: Add Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Contributing

1. Create feature branch
2. Implement feature with tests
3. Ensure all tests pass
4. Format and lint code
5. Update documentation
6. Submit for review

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI-MCP Documentation](https://fastapi-mcp.tadata.com/)
- [spaCy Documentation](https://spacy.io/)
- [Transformers Documentation](https://huggingface.co/docs/transformers/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Last Updated**: November 2024
