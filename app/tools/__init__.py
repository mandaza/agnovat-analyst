"""
MCP Tools for Agnovat Analyst
Implements all 23 tools for document analysis and QCAT appeal support
"""

from app.tools.pdf import router as pdf_router
from app.tools.analysis import router as analysis_router
from app.tools.legal import router as legal_router
from app.tools.reports import router as report_router

__all__ = [
    "pdf_router",
    "analysis_router",
    "legal_router",
    "report_router",
]
