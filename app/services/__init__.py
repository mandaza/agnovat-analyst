"""
Service layer for Agnovat Analyst
Business logic and processing services
"""

from app.services.pdf_service import (
    extract_text_from_pdf,
    generate_hash,
    verify_integrity,
    extract_metadata,
)
from app.services.nlp_service import (
    analyze_for_bias_and_racism,
    BiasDetector,
)
from app.services.document_analysis_service import (
    detect_inconsistent_statements,
    detect_template_reuse,
    detect_omitted_context,
    detect_non_evidence_based_statements,
)
from app.services.evidence_extraction_service import (
    extract_family_support_evidence,
    extract_public_guardian_limitations,
)
from app.services.comparison_timeline_service import (
    compare_pdf_documents,
    analyze_and_compare_pdfs,
    extract_timeline_events,
    generate_contradiction_matrix,
)
from app.services.legal_framework_service import (
    extract_human_rights_breaches,
    analyze_guardianship_risk,
    detect_state_guardianship_bias,
    analyze_professional_compliance,
)
from app.services.ndis_goals_service import (
    analyze_goals_guardianship_alignment,
)
from app.services.report_generation_service import (
    generate_guardianship_argument_report,
    generate_qcat_evidence_summary,
    generate_qcat_bundle,
)

__all__ = [
    "extract_text_from_pdf",
    "generate_hash",
    "verify_integrity",
    "extract_metadata",
    "analyze_for_bias_and_racism",
    "BiasDetector",
    "detect_inconsistent_statements",
    "detect_template_reuse",
    "detect_omitted_context",
    "detect_non_evidence_based_statements",
    "extract_family_support_evidence",
    "extract_public_guardian_limitations",
    "compare_pdf_documents",
    "analyze_and_compare_pdfs",
    "extract_timeline_events",
    "generate_contradiction_matrix",
    "extract_human_rights_breaches",
    "analyze_guardianship_risk",
    "detect_state_guardianship_bias",
    "analyze_professional_compliance",
    "analyze_goals_guardianship_alignment",
    "generate_guardianship_argument_report",
    "generate_qcat_evidence_summary",
    "generate_qcat_bundle",
]
