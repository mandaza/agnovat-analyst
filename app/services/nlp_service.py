"""
NLP Analysis Service
Handles bias, racism, and discriminatory language detection
"""

import re
from typing import List, Dict, Tuple
from loguru import logger
import spacy
from collections import defaultdict

from app.models.base import FlaggedSegment, RiskScore
from app.models.analysis import BiasAnalysisRequest, BiasAnalysisResponse
from app.config import settings


# Load spaCy model
try:
    nlp = spacy.load(settings.SPACY_MODEL)
    logger.info(f"Loaded spaCy model: {settings.SPACY_MODEL}")
except Exception as e:
    logger.warning(f"Could not load spaCy model: {e}")
    nlp = None


class BiasDetector:
    """Detects various forms of bias, racism, and discriminatory language"""

    # Explicit racism indicators
    EXPLICIT_RACISM_PATTERNS = [
        r"\brace(?:ial)?\s+(?:card|issue|problem)\b",
        r"\bplay(?:ing)?\s+the\s+race\s+card\b",
        r"\bthey\s+all\s+(?:look|act|behave)\b",
        r"\bthose\s+people\b",
        r"\btypical\s+(?:indigenous|aboriginal|ethnic)\b",
        r"\bnot\s+like\s+us\b",
        r"\btheir\s+(?:kind|type|culture)\s+(?:is|are)\b",
    ]

    # Implicit bias indicators
    IMPLICIT_BIAS_PATTERNS = [
        r"\balways\s+(?:aggressive|angry|violent|difficult)\b",
        r"\bnever\s+(?:cooperative|compliant|reasonable)\b",
        r"\bcannot\s+(?:understand|comprehend|follow)\b",
        r"\bunwilling\s+to\s+(?:engage|participate|cooperate)\b",
        r"\bfails\s+to\s+(?:understand|comply|engage)\b",
        r"\brefuses\s+to\s+(?:cooperate|engage|participate)\b",
        r"\black\s+of\s+(?:insight|understanding|awareness)\b",
        r"\bpoor\s+(?:judgment|decision-making|choices)\b",
    ]

    # Cultural insensitivity patterns
    CULTURAL_INSENSITIVITY_PATTERNS = [
        r"\bcultural\s+(?:barriers|limitations|issues)\b",
        r"\blanguage\s+(?:barriers|problems|difficulties)\b",
        r"\bfamily\s+dysfunction\b",
        r"\bchaotic\s+(?:family|household|environment)\b",
        r"\black\s+of\s+(?:parenting|family)\s+skills\b",
        r"\binappropriate\s+cultural\s+(?:practices|beliefs)\b",
        r"\b(?:backward|primitive|traditional)\s+beliefs\b",
        r"\bunusual\s+(?:cultural|family)\s+practices\b",
    ]

    # Stigmatizing language
    STIGMATIZING_LANGUAGE = [
        r"\bsuffering\s+from\b",
        r"\bafflicted\s+by\b",
        r"\bvictim\s+of\b",
        r"\bburdened\s+by\b",
        r"\bdifficult\s+(?:client|person|individual)\b",
        r"\bchallenging\s+(?:client|person|individual)\b",
        r"\bnon-compliant\b",
        r"\buncooperative\b",
        r"\bmanipulative\b",
        r"\battention-seeking\b",
        r"\bdemanding\b",
    ]

    # Deficit-focused language (focusing on problems not strengths)
    DEFICIT_LANGUAGE = [
        r"\bcannot\s+(?:\w+)\b",
        r"\bunable\s+to\s+(?:\w+)\b",
        r"\bfails\s+to\s+(?:\w+)\b",
        r"\bdeficit(?:s)?\s+in\b",
        r"\black(?:s)?\s+of\b",
        r"\bimpaired\b",
        r"\binadequate\b",
        r"\binsufficient\b",
    ]

    # Family capability undermining language
    FAMILY_UNDERMINING_PATTERNS = [
        r"\bfamily\s+(?:unable|incapable|cannot)\b",
        r"\bparents?\s+(?:lack|unable|cannot|fail)\b",
        r"\bfamily\s+(?:dysfunction|chaos|instability)\b",
        r"\binadequate\s+(?:parenting|family\s+support)\b",
        r"\bparents?\s+(?:do\s+not|don't)\s+understand\b",
        r"\bfamily\s+(?:does\s+not|doesn't)\s+(?:provide|offer|support)\b",
    ]

    @classmethod
    def detect_explicit_racism(cls, text: str, context_window: int = 100) -> List[FlaggedSegment]:
        """Detect explicit racist language"""
        flagged = []

        for pattern in cls.EXPLICIT_RACISM_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, match.start() - context_window)
                end = min(len(text), match.end() + context_window)
                context = text[start:end]

                flagged.append(FlaggedSegment(
                    text=match.group(),
                    page_number=0,  # Will be updated with actual page
                    context=context,
                    severity="critical",
                    category="explicit_racism",
                    explanation="Explicit racist or discriminatory language detected"
                ))

        return flagged

    @classmethod
    def detect_implicit_bias(cls, text: str, context_window: int = 100) -> List[FlaggedSegment]:
        """Detect implicit bias indicators"""
        flagged = []

        for pattern in cls.IMPLICIT_BIAS_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, match.start() - context_window)
                end = min(len(text), match.end() + context_window)
                context = text[start:end]

                flagged.append(FlaggedSegment(
                    text=match.group(),
                    page_number=0,
                    context=context,
                    severity="high",
                    category="implicit_bias",
                    explanation="Language suggesting implicit bias or stereotyping"
                ))

        return flagged

    @classmethod
    def detect_cultural_insensitivity(cls, text: str, context_window: int = 100) -> List[FlaggedSegment]:
        """Detect culturally insensitive language"""
        flagged = []

        for pattern in cls.CULTURAL_INSENSITIVITY_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, match.start() - context_window)
                end = min(len(text), match.end() + context_window)
                context = text[start:end]

                flagged.append(FlaggedSegment(
                    text=match.group(),
                    page_number=0,
                    context=context,
                    severity="high",
                    category="cultural_insensitivity",
                    explanation="Culturally insensitive or dismissive language"
                ))

        return flagged

    @classmethod
    def detect_stigmatizing_language(cls, text: str, context_window: int = 100) -> List[FlaggedSegment]:
        """Detect stigmatizing language"""
        flagged = []

        for pattern in cls.STIGMATIZING_LANGUAGE:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, match.start() - context_window)
                end = min(len(text), match.end() + context_window)
                context = text[start:end]

                flagged.append(FlaggedSegment(
                    text=match.group(),
                    page_number=0,
                    context=context,
                    severity="medium",
                    category="stigmatizing_language",
                    explanation="Stigmatizing or negative language about the client"
                ))

        return flagged

    @classmethod
    def detect_deficit_language(cls, text: str, context_window: int = 100) -> List[FlaggedSegment]:
        """Detect deficit-focused language"""
        flagged = []

        for pattern in cls.DEFICIT_LANGUAGE:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, match.start() - context_window)
                end = min(len(text), match.end() + context_window)
                context = text[start:end]

                flagged.append(FlaggedSegment(
                    text=match.group(),
                    page_number=0,
                    context=context,
                    severity="low",
                    category="deficit_language",
                    explanation="Deficit-focused language; lacks strength-based perspective"
                ))

        return flagged

    @classmethod
    def detect_family_undermining(cls, text: str, context_window: int = 100) -> List[FlaggedSegment]:
        """Detect language that undermines family capability"""
        flagged = []

        for pattern in cls.FAMILY_UNDERMINING_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, match.start() - context_window)
                end = min(len(text), match.end() + context_window)
                context = text[start:end]

                flagged.append(FlaggedSegment(
                    text=match.group(),
                    page_number=0,
                    context=context,
                    severity="high",
                    category="family_undermining",
                    explanation="Language that undermines family capacity without evidence"
                ))

        return flagged


def calculate_risk_scores(flagged_segments: List[FlaggedSegment]) -> Dict[str, RiskScore]:
    """Calculate risk scores by category"""
    category_counts = defaultdict(int)
    category_severities = defaultdict(list)

    severity_weights = {
        "low": 1,
        "medium": 3,
        "high": 7,
        "critical": 10
    }

    for segment in flagged_segments:
        category_counts[segment.category] += 1
        category_severities[segment.category].append(severity_weights[segment.severity])

    risk_scores = {}
    for category, count in category_counts.items():
        avg_severity = sum(category_severities[category]) / len(category_severities[category])

        # Score calculation: frequency + severity
        score = min(10.0, (count * 0.5) + avg_severity)
        confidence = min(1.0, count / 10)  # More instances = higher confidence

        risk_scores[category] = RiskScore(
            category=category.replace("_", " ").title(),
            score=round(score, 2),
            confidence=round(confidence, 2),
            evidence=[f'"{seg.text}"' for seg in flagged_segments if seg.category == category][:5]
        )

    return risk_scores


def generate_narrative_report(
    flagged_segments: List[FlaggedSegment],
    risk_scores: Dict[str, RiskScore],
    client_name: str = None
) -> str:
    """Generate a narrative report for QCAT"""

    client_ref = f"regarding {client_name}" if client_name else "in this document"

    report_parts = [
        f"# Bias and Discrimination Analysis Report\n",
        f"\n## Executive Summary\n",
        f"This analysis identified {len(flagged_segments)} instances of potentially ",
        f"biased, discriminatory, or problematic language {client_ref}.\n",
    ]

    if not flagged_segments:
        report_parts.append("\nNo significant bias indicators were detected.")
        return "".join(report_parts)

    # Overall severity
    severities = [seg.severity for seg in flagged_segments]
    if "critical" in severities:
        overall = "CRITICAL"
    elif severities.count("high") > 3:
        overall = "HIGH"
    elif severities.count("medium") > 5:
        overall = "MEDIUM"
    else:
        overall = "LOW"

    report_parts.append(f"\n**Overall Severity Level:** {overall}\n")

    # Categories detected
    categories = set(seg.category for seg in flagged_segments)
    report_parts.append(f"\n**Categories Detected:** {len(categories)}\n")

    # Detailed findings by category
    report_parts.append("\n## Detailed Findings\n")

    for category, risk_score in risk_scores.items():
        category_segments = [s for s in flagged_segments if s.category == category.lower().replace(" ", "_")]

        report_parts.append(f"\n### {category}\n")
        report_parts.append(f"- **Risk Score:** {risk_score.score}/10\n")
        report_parts.append(f"- **Confidence:** {risk_score.confidence * 100:.0f}%\n")
        report_parts.append(f"- **Instances Found:** {len(category_segments)}\n")

        if category_segments:
            report_parts.append(f"\n**Examples:**\n")
            for i, seg in enumerate(category_segments[:3], 1):
                report_parts.append(f'{i}. "{seg.text}"\n')
                report_parts.append(f"   - {seg.explanation}\n")

    # QCAT relevance
    report_parts.append("\n## Relevance to QCAT Appeal\n")
    report_parts.append(
        "These findings are relevant to Queensland Civil and Administrative Tribunal "
        "proceedings under:\n\n"
        "- **Human Rights Act 2019 (Qld)** s15 (Freedom of expression), s26 (Cultural rights)\n"
        "- **Anti-Discrimination Act 1991 (Qld)** regarding racial discrimination\n"
        "- **Racial Discrimination Act 1975 (Cth)** s9 and s18C\n"
        "- **Guardianship principles** requiring unbiased, evidence-based assessment\n\n"
        "The identified language patterns may indicate:\n"
        "- Bias in assessment\n"
        "- Discriminatory treatment\n"
        "- Failure to consider cultural context\n"
        "- Undermining of family capacity without evidence\n"
    )

    return "".join(report_parts)


async def analyze_for_bias_and_racism(request: BiasAnalysisRequest) -> BiasAnalysisResponse:
    """
    Main function to analyze PDF for bias and racism
    """
    from app.services.pdf_service import extract_text_from_pdf
    from app.models.pdf import PDFExtractionRequest

    try:
        # Extract text from PDF
        logger.info(f"Analyzing document for bias: {request.file_path}")
        pdf_request = PDFExtractionRequest(
            file_path=request.file_path,
            extract_metadata=False
        )
        pdf_result = await extract_text_from_pdf(pdf_request)

        full_text = pdf_result.full_text

        # Run all detection methods
        all_flagged_segments = []

        all_flagged_segments.extend(BiasDetector.detect_explicit_racism(full_text))
        all_flagged_segments.extend(BiasDetector.detect_implicit_bias(full_text))
        all_flagged_segments.extend(BiasDetector.detect_cultural_insensitivity(full_text))
        all_flagged_segments.extend(BiasDetector.detect_stigmatizing_language(full_text))
        all_flagged_segments.extend(BiasDetector.detect_deficit_language(full_text))
        all_flagged_segments.extend(BiasDetector.detect_family_undermining(full_text))

        # Map segments to actual page numbers
        for segment in all_flagged_segments:
            for page in pdf_result.pages:
                if segment.text.lower() in page.text.lower():
                    segment.page_number = page.page_number
                    break

        # Calculate risk scores
        risk_scores = calculate_risk_scores(all_flagged_segments)

        # Determine overall severity
        if any(seg.severity == "critical" for seg in all_flagged_segments):
            overall_severity = "critical"
        elif len([s for s in all_flagged_segments if s.severity == "high"]) > 3:
            overall_severity = "high"
        elif len([s for s in all_flagged_segments if s.severity == "medium"]) > 5:
            overall_severity = "medium"
        else:
            overall_severity = "low"

        # Generate narrative report
        narrative_report = generate_narrative_report(
            all_flagged_segments,
            risk_scores,
            request.client_name
        )

        # Get unique categories
        categories_detected = list(set(seg.category for seg in all_flagged_segments))

        logger.info(f"Analysis complete: Found {len(all_flagged_segments)} flagged segments")

        return BiasAnalysisResponse(
            file_path=request.file_path,
            risk_scores=risk_scores,
            flagged_segments=all_flagged_segments,
            narrative_report=narrative_report,
            overall_severity=overall_severity,
            categories_detected=categories_detected
        )

    except Exception as e:
        logger.error(f"Error in bias analysis: {str(e)}")
        raise
