"""
Agnovat Analyst MCP Server
Document Integrity, Racism, Bias & Guardianship Alignment Analysis
For QCAT Guardianship Appeal Support
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP
from loguru import logger

from app.config import settings
from app.tools import pdf_router, analysis_router, legal_router, report_router


# Initialize FastAPI application
app = FastAPI(
    title="Agnovat Analyst MCP Server",
    description="Document Integrity, Racism, Bias & Guardianship Alignment Analysis for QCAT Appeals",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for different tool categories
app.include_router(pdf_router, prefix="/api/pdf", tags=["PDF Processing"])
app.include_router(analysis_router, prefix="/api/analysis", tags=["Document Analysis"])
app.include_router(legal_router, prefix="/api/legal", tags=["Legal Framework"])
app.include_router(report_router, prefix="/api/reports", tags=["Report Generation"])

# Initialize FastAPI-MCP
mcp = FastApiMCP(app)
mcp.mount_http()

logger.info("Agnovat Analyst MCP Server initialized")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - Health check"""
    return {
        "service": "Agnovat Analyst MCP Server",
        "version": "1.0.0",
        "status": "operational",
        "purpose": "QCAT Guardianship Appeal Support",
        "mcp_endpoint": "/mcp",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "agnovat-analyst",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
