"""
Comparison and Timeline Service
Tools 12-15: Document Comparison, Timeline Extraction, Contradiction Matrix
"""

import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher
from loguru import logger

from app.models.reports import (
    ComparisonReportRequest,
    ComparisonReportResponse,
    DocumentDifference,
    TimelineExtractionRequest,
    TimelineExtractionResponse,
    TimelineEvent,
    ContradictionMatrixRequest,
    ContradictionMatrixResponse,
    ContradictionMatrixRow,
)
from app.services.pdf_service import extract_text_from_pdf
from app.services.nlp_service import analyze_for_bias_and_racism
from app.models.pdf import PDFExtractionRequest
from app.models.analysis import BiasAnalysisRequest


# ============================================================================
# TOOL 12: DOCUMENT COMPARISON
# ============================================================================

class DocumentComparator:
    """Compares two documents and identifies differences"""

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Calculate overall text similarity percentage"""
        matcher = SequenceMatcher(None, text1, text2)
        return matcher.ratio() * 100

    @staticmethod
    def find_unique_content(text1: str, text2: str, min_length: int = 50) -> List[str]:
        """Find content unique to one document"""
        unique_blocks = []

        # Split into sentences
        sentences1 = re.split(r'[.!?]+', text1)
        sentences2 = re.split(r'[.!?]+', text2)

        for sentence in sentences1:
            sentence = sentence.strip()
            if len(sentence) > min_length:
                # Check if this sentence appears in doc2
                if sentence.lower() not in text2.lower():
                    unique_blocks.append(sentence)

        return unique_blocks[:10]  # Limit to top 10

    @staticmethod
    def identify_key_differences(text1: str, text2: str) -> List[DocumentDifference]:
        """Identify key categorical differences"""
        differences = []

        # Check for recommendation differences
        rec_pattern = r'recommend(?:s|ation)?[:\s]+([^.!?]+)'
        recs1 = re.findall(rec_pattern, text1, re.IGNORECASE)
        recs2 = re.findall(rec_pattern, text2, re.IGNORECASE)

        if recs1 and recs2:
            if recs1[0].lower() != recs2[0].lower():
                differences.append(DocumentDifference(
                    category="recommendation",
                    description="Different recommendations between documents",
                    document_a_content=recs1[0][:200],
                    document_b_content=recs2[0][:200],
                    page_a=None,
                    page_b=None,
                    significance="high"
                ))

        # Check for risk assessment differences
        risk_keywords = ['risk', 'danger', 'concern', 'issue', 'problem']
        risk_count_1 = sum(len(re.findall(rf'\b{kw}\b', text1, re.IGNORECASE)) for kw in risk_keywords)
        risk_count_2 = sum(len(re.findall(rf'\b{kw}\b', text2, re.IGNORECASE)) for kw in risk_keywords)

        if abs(risk_count_1 - risk_count_2) > 5:
            differences.append(DocumentDifference(
                category="risk_assessment",
                description="Significant difference in risk language",
                document_a_content=f"{risk_count_1} risk-related terms",
                document_b_content=f"{risk_count_2} risk-related terms",
                page_a=None,
                page_b=None,
                significance="medium"
            ))

        # Check for family mention differences
        family_keywords = ['family', 'parent', 'mother', 'father', 'sibling']
        family_count_1 = sum(len(re.findall(rf'\b{kw}\b', text1, re.IGNORECASE)) for kw in family_keywords)
        family_count_2 = sum(len(re.findall(rf'\b{kw}\b', text2, re.IGNORECASE)) for kw in family_keywords)

        if abs(family_count_1 - family_count_2) > 5:
            differences.append(DocumentDifference(
                category="family_involvement",
                description="Different emphasis on family involvement",
                document_a_content=f"{family_count_1} family-related mentions",
                document_b_content=f"{family_count_2} family-related mentions",
                page_a=None,
                page_b=None,
                significance="medium"
            ))

        return differences


async def compare_pdf_documents(request: ComparisonReportRequest) -> ComparisonReportResponse:
    """
    Tool 12: Compare two practitioner reports and highlight differences
    """
    try:
        logger.info(f"Comparing documents: {request.file_a} vs {request.file_b}")

        # Extract text from both documents
        pdf_request_a = PDFExtractionRequest(file_path=request.file_a, extract_metadata=False)
        pdf_request_b = PDFExtractionRequest(file_path=request.file_b, extract_metadata=False)

        pdf_result_a = await extract_text_from_pdf(pdf_request_a)
        pdf_result_b = await extract_text_from_pdf(pdf_request_b)

        text_a = pdf_result_a.full_text
        text_b = pdf_result_b.full_text

        # Calculate similarity
        similarity_score = DocumentComparator.calculate_similarity(text_a, text_b)

        # Find unique content
        unique_content_a = DocumentComparator.find_unique_content(text_a, text_b)
        unique_content_b = DocumentComparator.find_unique_content(text_b, text_a)

        # Identify key differences
        differences = DocumentComparator.identify_key_differences(text_a, text_b)

        # Generate diff summary
        diff_summary = (
            f"Documents are {similarity_score:.1f}% similar. "
            f"Found {len(differences)} key differences. "
            f"{len(unique_content_a)} sections unique to {request.document_a_label}, "
            f"{len(unique_content_b)} sections unique to {request.document_b_label}."
        )

        # Generate narrative report
        narrative_parts = [
            f"## Document Comparison Report\n\n",
            f"**{request.document_a_label}:** {request.file_a}\n",
            f"**{request.document_b_label}:** {request.file_b}\n\n",
            f"### Overall Similarity\n",
            f"The documents are **{similarity_score:.1f}% similar**.\n\n",
        ]

        if differences:
            narrative_parts.append(f"### Key Differences\n\n")
            for diff in differences:
                narrative_parts.append(f"**{diff.category.replace('_', ' ').title()}** ({diff.significance} significance)\n")
                narrative_parts.append(f"- {diff.description}\n")
                narrative_parts.append(f"- {request.document_a_label}: {diff.document_a_content}\n")
                narrative_parts.append(f"- {request.document_b_label}: {diff.document_b_content}\n\n")

        if unique_content_a:
            narrative_parts.append(f"### Content Unique to {request.document_a_label}\n\n")
            for content in unique_content_a[:3]:
                narrative_parts.append(f"- {content}\n")
            narrative_parts.append("\n")

        if unique_content_b:
            narrative_parts.append(f"### Content Unique to {request.document_b_label}\n\n")
            for content in unique_content_b[:3]:
                narrative_parts.append(f"- {content}\n")

        narrative_report = "".join(narrative_parts)

        logger.info(f"Comparison complete: {similarity_score:.1f}% similar, {len(differences)} differences")

        return ComparisonReportResponse(
            document_a=request.file_a,
            document_b=request.file_b,
            similarity_score=round(similarity_score, 2),
            differences=differences,
            unique_content_a=unique_content_a,
            unique_content_b=unique_content_b,
            diff_summary=diff_summary,
            narrative_report=narrative_report
        )

    except Exception as e:
        logger.error(f"Error comparing documents: {str(e)}")
        raise


# ============================================================================
# TOOL 13: ANALYZE AND COMPARE
# ============================================================================

async def analyze_and_compare_pdfs(request: ComparisonReportRequest) -> ComparisonReportResponse:
    """
    Tool 13: Full analysis + comparison of two documents in a single tool

    Combines bias analysis with document comparison
    """
    try:
        logger.info(f"Analyzing and comparing: {request.file_a} vs {request.file_b}")

        # First, do standard comparison
        comparison_result = await compare_pdf_documents(request)

        # Then run bias analysis on both documents
        bias_request_a = BiasAnalysisRequest(file_path=request.file_a, client_name=None)
        bias_request_b = BiasAnalysisRequest(file_path=request.file_b, client_name=None)

        try:
            bias_result_a = await analyze_for_bias_and_racism(bias_request_a)
            bias_result_b = await analyze_for_bias_and_racism(bias_request_b)

            # Add bias comparison to differences
            bias_diff = DocumentDifference(
                category="bias_analysis",
                description="Bias severity comparison",
                document_a_content=f"Overall severity: {bias_result_a.overall_severity}, {len(bias_result_a.flagged_segments)} flagged segments",
                document_b_content=f"Overall severity: {bias_result_b.overall_severity}, {len(bias_result_b.flagged_segments)} flagged segments",
                page_a=None,
                page_b=None,
                significance="high" if bias_result_a.overall_severity != bias_result_b.overall_severity else "medium"
            )

            comparison_result.differences.append(bias_diff)

            # Update narrative with bias analysis
            bias_narrative = (
                f"\n\n### Bias Analysis Comparison\n\n"
                f"**{request.document_a_label}:**\n"
                f"- Overall Severity: {bias_result_a.overall_severity}\n"
                f"- Flagged Segments: {len(bias_result_a.flagged_segments)}\n"
                f"- Categories: {', '.join(bias_result_a.categories_detected)}\n\n"
                f"**{request.document_b_label}:**\n"
                f"- Overall Severity: {bias_result_b.overall_severity}\n"
                f"- Flagged Segments: {len(bias_result_b.flagged_segments)}\n"
                f"- Categories: {', '.join(bias_result_b.categories_detected)}\n\n"
            )

            comparison_result.narrative_report += bias_narrative

        except Exception as e:
            logger.warning(f"Bias analysis failed during comparison: {str(e)}")

        logger.info("Combined analysis and comparison complete")
        return comparison_result

    except Exception as e:
        logger.error(f"Error in analyze_and_compare: {str(e)}")
        raise


# ============================================================================
# TOOL 14: TIMELINE EXTRACTION
# ============================================================================

class TimelineExtractor:
    """Extracts timeline events from documents"""

    DATE_PATTERNS = [
        (r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b', 'DD/MM/YYYY'),
        (r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b', 'YYYY/MM/DD'),
        (r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(\d{4})\b', 'Month DD, YYYY'),
        (r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\b', 'DD Month YYYY'),
    ]

    MONTH_MAP = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }

    @classmethod
    def parse_date(cls, date_str: str, format_type: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        try:
            if format_type == 'DD/MM/YYYY':
                parts = re.split(r'[/-]', date_str)
                return datetime(int(parts[2]), int(parts[1]), int(parts[0]))
            elif format_type == 'YYYY/MM/DD':
                parts = re.split(r'[/-]', date_str)
                return datetime(int(parts[0]), int(parts[1]), int(parts[2]))
            elif format_type == 'Month DD, YYYY':
                match = re.match(r'([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})', date_str)
                if match:
                    month = cls.MONTH_MAP.get(match.group(1)[:3].lower())
                    if month:
                        return datetime(int(match.group(3)), month, int(match.group(2)))
            elif format_type == 'DD Month YYYY':
                match = re.match(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', date_str)
                if match:
                    month = cls.MONTH_MAP.get(match.group(2)[:3].lower())
                    if month:
                        return datetime(int(match.group(3)), month, int(match.group(1)))
        except:
            pass
        return None

    @classmethod
    def extract_timeline(cls, text: str) -> List[TimelineEvent]:
        """Extract timeline events from text"""
        events = []

        for pattern, format_type in cls.DATE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                date_str = match.group()
                date_obj = cls.parse_date(date_str, format_type)

                if date_obj:
                    # Extract context around the date
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end].strip()

                    # Extract event description (sentence containing the date)
                    sentence_start = text.rfind('.', 0, match.start()) + 1
                    sentence_end = text.find('.', match.end())
                    if sentence_end == -1:
                        sentence_end = len(text)

                    event_desc = text[sentence_start:sentence_end].strip()

                    # Categorize event
                    category = cls._categorize_event(event_desc)

                    # Assess significance
                    significance = cls._assess_significance(event_desc)

                    events.append(TimelineEvent(
                        date=date_obj,
                        event=event_desc[:200],  # Limit length
                        source=f"Document (approx. char {match.start()})",
                        category=category,
                        significance=significance
                    ))

        # Sort by date
        events.sort(key=lambda x: x.date)

        # Remove duplicates
        unique_events = []
        seen = set()
        for event in events:
            key = (event.date.date(), event.event[:50])
            if key not in seen:
                seen.add(key)
                unique_events.append(event)

        return unique_events

    @staticmethod
    def _categorize_event(event_text: str) -> str:
        """Categorize event based on content"""
        event_lower = event_text.lower()

        if any(word in event_lower for word in ['appointment', 'meeting', 'visit', 'consultation']):
            return "appointment"
        elif any(word in event_lower for word in ['assessment', 'evaluation', 'review']):
            return "assessment"
        elif any(word in event_lower for word in ['incident', 'event', 'occurred', 'happened']):
            return "incident"
        elif any(word in event_lower for word in ['decision', 'determination', 'ruling']):
            return "decision"
        elif any(word in event_lower for word in ['report', 'document', 'letter']):
            return "documentation"
        else:
            return "other"

    @staticmethod
    def _assess_significance(event_text: str) -> str:
        """Assess significance of event"""
        event_lower = event_text.lower()

        high_significance_keywords = [
            'guardianship', 'transfer', 'appointment', 'decision', 'determination',
            'critical', 'significant', 'major', 'important'
        ]

        if any(keyword in event_lower for keyword in high_significance_keywords):
            return "high"
        elif len(event_text) > 100:
            return "medium"
        else:
            return "low"


async def extract_timeline_events(request: TimelineExtractionRequest) -> TimelineExtractionResponse:
    """
    Tool 14: Extract all date+event pairs to build a timeline
    """
    try:
        logger.info(f"Extracting timeline from: {request.file_path}")

        # Extract text
        pdf_request = PDFExtractionRequest(file_path=request.file_path, extract_metadata=False)
        pdf_result = await extract_text_from_pdf(pdf_request)

        # Extract timeline
        timeline = TimelineExtractor.extract_timeline(pdf_result.full_text)

        # Calculate date range
        if timeline:
            date_range = (timeline[0].date, timeline[-1].date)
        else:
            date_range = (None, None)

        logger.info(f"Extracted {len(timeline)} timeline events")

        return TimelineExtractionResponse(
            file_path=request.file_path,
            timeline=timeline,
            total_events=len(timeline),
            date_range=date_range
        )

    except Exception as e:
        logger.error(f"Error extracting timeline: {str(e)}")
        raise


# ============================================================================
# TOOL 15: CONTRADICTION MATRIX
# ============================================================================

async def generate_contradiction_matrix(request: ContradictionMatrixRequest) -> ContradictionMatrixResponse:
    """
    Tool 15: Create structured contradictions table
    """
    try:
        logger.info(f"Generating contradiction matrix for {len(request.documents)} documents")

        # Extract text from all documents
        documents_data = []
        for doc_path in request.documents:
            pdf_request = PDFExtractionRequest(file_path=doc_path, extract_metadata=False)
            pdf_result = await extract_text_from_pdf(pdf_request)
            documents_data.append({
                'path': doc_path,
                'text': pdf_result.full_text
            })

        matrix = []

        if len(documents_data) >= 2:
            doc1 = documents_data[0]
            doc2 = documents_data[1]

            # Find contradictions in behavioral assessments
            behaviors = [
                ("cooperative", "uncooperative"),
                ("aggressive", "calm"),
                ("compliant", "non-compliant"),
                ("stable", "unstable"),
                ("capable", "incapable"),
            ]

            for positive, negative in behaviors:
                has_pos_1 = bool(re.search(rf'\b{positive}\b', doc1['text'], re.IGNORECASE))
                has_neg_1 = bool(re.search(rf'\b{negative}\b', doc1['text'], re.IGNORECASE))
                has_pos_2 = bool(re.search(rf'\b{positive}\b', doc2['text'], re.IGNORECASE))
                has_neg_2 = bool(re.search(rf'\b{negative}\b', doc2['text'], re.IGNORECASE))

                if (has_pos_1 and has_neg_2) or (has_neg_1 and has_pos_2):
                    matrix.append(ContradictionMatrixRow(
                        topic=f"Behavioral assessment: {positive}/{negative}",
                        version_1=f"Described as {positive if has_pos_1 else negative}",
                        version_2=f"Described as {positive if has_pos_2 else negative}",
                        conflict="Contradictory behavioral characterization",
                        explanation=f"Document 1 characterizes client as {positive if has_pos_1 else negative}, while Document 2 characterizes as {positive if has_pos_2 else negative}",
                        source_1=doc1['path'],
                        source_2=doc2['path']
                    ))

        summary = f"Generated contradiction matrix with {len(matrix)} rows comparing {len(request.documents)} documents."

        logger.info(f"Matrix generated: {len(matrix)} contradictions found")

        return ContradictionMatrixResponse(
            documents=request.documents,
            matrix=matrix,
            total_contradictions=len(matrix),
            summary=summary
        )

    except Exception as e:
        logger.error(f"Error generating contradiction matrix: {str(e)}")
        raise
