"""
Evidence Extraction Service
Tools 10-11: Family Support Evidence & Public Guardian Limitations
"""

import re
from typing import List, Dict
from loguru import logger

from app.models.base import EvidenceItem
from app.models.analysis import (
    FamilySupportEvidenceRequest,
    FamilySupportEvidenceResponse,
    FamilySupportThemes,
)
from app.services.pdf_service import extract_text_from_pdf
from app.models.pdf import PDFExtractionRequest


# ============================================================================
# TOOL 10: FAMILY SUPPORT EVIDENCE EXTRACTION
# ============================================================================

class FamilyEvidenceExtractor:
    """Extracts evidence of family support and involvement"""

    # Family support patterns by theme
    EMOTIONAL_SUPPORT_PATTERNS = [
        r"family\s+(?:provides?|offers?|gives?)\s+(?:emotional|affective)\s+support",
        r"(?:mother|father|parent|sibling)s?\s+(?:comforts?|reassures?|calms?)",
        r"family\s+(?:helps?|assists?)\s+(?:with|manage)\s+(?:emotions?|feelings?)",
        r"(?:mother|father|parent)s?\s+(?:understands?|recogni[sz]es?)\s+(?:when|if)",
        r"emotional\s+(?:bond|connection)\s+with\s+family",
        r"family\s+(?:presence|support)\s+(?:calms?|settles?|soothes?)",
        r"(?:mother|father|parent)s?\s+(?:de-escalates?|prevents?)\s+(?:crisis|meltdown)",
        r"family\s+(?:knows?|understands?)\s+(?:client|triggers|needs?)",
    ]

    COMMUNITY_SUPPORT_PATTERNS = [
        r"family\s+(?:facilitates?|enables?|supports?)\s+(?:community|social)",
        r"(?:mother|father|parent)s?\s+(?:takes?|brings?)\s+to\s+(?:events?|activities?)",
        r"family\s+(?:connection|involvement)\s+(?:in|with)\s+community",
        r"(?:mother|father|parent)s?\s+(?:organiz|arrang)es?\s+(?:social|community)",
        r"family\s+(?:helps?|assists?)\s+(?:maintain|build)\s+(?:friendships?|relationships?)",
        r"(?:mother|father|parent)s?\s+(?:supports?|encourages?)\s+(?:participation|involvement)",
    ]

    DAILY_LIVING_PATTERNS = [
        r"family\s+(?:assists?|helps?|supports?)\s+with\s+(?:daily|everyday)",
        r"(?:mother|father|parent)s?\s+(?:cooks?|prepares?)\s+meals?",
        r"(?:mother|father|parent)s?\s+(?:helps?|assists?)\s+with\s+(?:hygiene|grooming|dressing)",
        r"family\s+(?:manages?|organizes?)\s+(?:medication|appointments?)",
        r"(?:mother|father|parent)s?\s+(?:provides?|arranges?)\s+(?:transport|transportation)",
        r"family\s+(?:maintains?|keeps?)\s+(?:routine|schedule|structure)",
        r"(?:mother|father|parent)s?\s+(?:monitors?|supervises?|oversees?)",
    ]

    CULTURAL_SUPPORT_PATTERNS = [
        r"family\s+(?:maintains?|preserves?|supports?)\s+(?:cultural|traditional)",
        r"(?:mother|father|parent)s?\s+(?:teaches?|shares?)\s+(?:language|culture|traditions?)",
        r"family\s+(?:connection|involvement)\s+(?:to|with)\s+(?:culture|community|country)",
        r"(?:mother|father|parent)s?\s+(?:facilitates?|enables?)\s+(?:cultural|traditional)\s+(?:practices?|events?)",
        r"family\s+(?:supports?|encourages?)\s+(?:cultural|traditional)\s+(?:identity|practices?)",
        r"(?:mother|father|parent)s?\s+(?:maintains?|supports?)\s+(?:connection|ties)\s+to\s+(?:family|community|culture)",
    ]

    EMPLOYMENT_SUPPORT_PATTERNS = [
        r"family\s+(?:supports?|assists?|helps?)\s+with\s+(?:work|employment|business)",
        r"(?:mother|father|parent)s?\s+(?:helps?|assists?)\s+(?:with|run|manage)\s+business",
        r"family\s+(?:provides?|offers?)\s+(?:work|employment)\s+(?:opportunities?|support)",
        r"(?:mother|father|parent)s?\s+(?:encourages?|supports?)\s+(?:independence|employment)",
        r"family\s+(?:assists?|helps?)\s+with\s+(?:job|career|work)",
    ]

    DECISION_MAKING_PATTERNS = [
        r"family\s+(?:supports?|assists?|helps?)\s+(?:with|in)\s+(?:decisions?|decision-making)",
        r"(?:mother|father|parent)s?\s+(?:consults?|discusses?)\s+with\s+(?:client|adult)",
        r"family\s+(?:respects?|honours?|follows?)\s+(?:wishes|preferences|choices?)",
        r"(?:mother|father|parent)s?\s+(?:advocates?|speaks?)\s+for",
        r"family\s+(?:understands?|knows?)\s+(?:preferences|wishes|wants)",
        r"(?:mother|father|parent)s?\s+(?:involves?|includes?)\s+(?:in|with)\s+decisions?",
    ]

    @classmethod
    def extract_by_theme(cls, text: str, patterns: List[str], theme: str, pages: List) -> List[EvidenceItem]:
        """Extract evidence items for a specific theme"""
        evidence_items = []

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Get context
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()

                # Find page number
                page_num = 0
                for page in pages:
                    if match.group().lower() in page.text.lower():
                        page_num = page.page_number
                        break

                # Calculate relevance score based on specificity
                specificity_indicators = [
                    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # dates
                    r'\b(?:specifically|example|instance)\b',  # specificity markers
                    r'\b(?:always|regularly|frequently|often)\b',  # frequency markers
                ]
                relevance_score = 0.5
                for indicator in specificity_indicators:
                    if re.search(indicator, context, re.IGNORECASE):
                        relevance_score += 0.15

                relevance_score = min(1.0, relevance_score)

                evidence_items.append(EvidenceItem(
                    text=match.group(),
                    page_number=page_num,
                    category=theme,
                    relevance_score=round(relevance_score, 2),
                    context=context
                ))

        return evidence_items


async def extract_family_support_evidence(
    request: FamilySupportEvidenceRequest
) -> FamilySupportEvidenceResponse:
    """
    Tool 10: Extract all mentions of family involvement and support
    """
    try:
        logger.info(f"Extracting family support evidence from: {request.file_path}")

        # Extract text from PDF
        pdf_request = PDFExtractionRequest(file_path=request.file_path, extract_metadata=False)
        pdf_result = await extract_text_from_pdf(pdf_request)

        text = pdf_result.full_text
        pages = pdf_result.pages

        # Extract evidence by theme
        emotional = FamilyEvidenceExtractor.extract_by_theme(
            text, FamilyEvidenceExtractor.EMOTIONAL_SUPPORT_PATTERNS, "emotional", pages
        )

        community = FamilyEvidenceExtractor.extract_by_theme(
            text, FamilyEvidenceExtractor.COMMUNITY_SUPPORT_PATTERNS, "community", pages
        )

        daily_living = FamilyEvidenceExtractor.extract_by_theme(
            text, FamilyEvidenceExtractor.DAILY_LIVING_PATTERNS, "daily_living", pages
        )

        cultural = FamilyEvidenceExtractor.extract_by_theme(
            text, FamilyEvidenceExtractor.CULTURAL_SUPPORT_PATTERNS, "cultural", pages
        )

        employment = FamilyEvidenceExtractor.extract_by_theme(
            text, FamilyEvidenceExtractor.EMPLOYMENT_SUPPORT_PATTERNS, "employment", pages
        )

        decision_making = FamilyEvidenceExtractor.extract_by_theme(
            text, FamilyEvidenceExtractor.DECISION_MAKING_PATTERNS, "decision_making", pages
        )

        # Combine all evidence
        all_evidence = emotional + community + daily_living + cultural + employment + decision_making

        # Create themes object
        themes = FamilySupportThemes(
            emotional=emotional,
            community=community,
            daily_living=daily_living,
            cultural=cultural,
            employment=employment,
            decision_making=decision_making
        )

        # Generate summary
        theme_counts = {
            "emotional": len(emotional),
            "community": len(community),
            "daily living": len(daily_living),
            "cultural": len(cultural),
            "employment": len(employment),
            "decision-making": len(decision_making),
        }

        summary_parts = [
            f"Found {len(all_evidence)} instances of family support across {len([c for c in theme_counts.values() if c > 0])} themes."
        ]

        if theme_counts:
            top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            summary_parts.append(
                f"Primary themes: {', '.join([f'{theme} ({count})' for theme, count in top_themes if count > 0])}."
            )

        summary = " ".join(summary_parts)

        logger.info(f"Extracted {len(all_evidence)} family support instances")

        return FamilySupportEvidenceResponse(
            file_path=request.file_path,
            family_support_instances=all_evidence,
            themes=themes,
            total_instances=len(all_evidence),
            summary=summary
        )

    except Exception as e:
        logger.error(f"Error extracting family support evidence: {str(e)}")
        raise


# ============================================================================
# TOOL 11: PUBLIC GUARDIAN LIMITATIONS EXTRACTION
# ============================================================================

class PublicGuardianLimitationsExtractor:
    """Extracts evidence of Public Guardian limitations and negative impacts"""

    # Public Guardian limitation patterns
    PG_BARRIER_PATTERNS = [
        r"public\s+guardian\s+(?:prevents?|blocks?|restricts?)",
        r"(?:unable|cannot)\s+(?:to\s+)?(?:contact|reach|speak\s+to)\s+(?:public\s+guardian|PG)",
        r"public\s+guardian\s+(?:delays?|postpones?)",
        r"(?:waiting|waited)\s+(?:for|on)\s+public\s+guardian",
        r"public\s+guardian\s+(?:does\s+not|doesn't)\s+(?:respond|reply|answer)",
        r"(?:lack\s+of|no)\s+(?:access|contact)\s+(?:to|with)\s+public\s+guardian",
    ]

    PG_FAMILY_SEPARATION_PATTERNS = [
        r"public\s+guardian\s+(?:limits?|restricts?|reduces?)\s+(?:family|parental)\s+(?:contact|involvement|access)",
        r"family\s+(?:excluded|not\s+involved|not\s+consulted)",
        r"public\s+guardian\s+(?:overrides?|ignores?|dismisses?)\s+family",
        r"(?:reduced|limited|restricted)\s+(?:family|parental)\s+(?:access|contact|involvement)",
        r"public\s+guardian\s+(?:decision|approach)\s+(?:conflicts?|contradicts?)\s+(?:with\s+)?family",
    ]

    PG_CULTURAL_DISCONNECT_PATTERNS = [
        r"public\s+guardian\s+(?:lacks?|does\s+not\s+understand)\s+(?:cultural|traditional)",
        r"(?:no|limited)\s+(?:cultural|traditional)\s+(?:understanding|knowledge|awareness)",
        r"public\s+guardian\s+(?:unfamiliar|unaware)\s+(?:with|of)\s+(?:cultural|traditional|community)",
        r"(?:cultural|traditional)\s+(?:disconnect|gap|barrier)",
        r"public\s+guardian\s+(?:does\s+not|doesn't)\s+(?:support|maintain)\s+(?:cultural|traditional)",
    ]

    PG_PERSONAL_KNOWLEDGE_PATTERNS = [
        r"public\s+guardian\s+(?:does\s+not|doesn't)\s+know",
        r"(?:lacks?|has\s+no)\s+(?:personal|detailed|intimate)\s+knowledge",
        r"public\s+guardian\s+(?:unfamiliar|unaware)\s+(?:with|of)\s+(?:client|preferences|history)",
        r"(?:does\s+not|doesn't)\s+understand\s+(?:client|needs|preferences|triggers)",
        r"public\s+guardian\s+(?:generic|impersonal|distant)",
    ]

    PG_GOAL_CONFLICT_PATTERNS = [
        r"public\s+guardian\s+(?:decision|approach)\s+(?:conflicts?|contradicts?)\s+(?:with\s+)?(?:goals?|wishes?|preferences?)",
        r"(?:inconsistent|incompatible)\s+with\s+(?:NDIS\s+)?goals?",
        r"public\s+guardian\s+(?:prevents?|blocks?|hinders?)\s+(?:progress|achievement|goals?)",
        r"(?:undermines?|jeopardi[sz]es?)\s+(?:NDIS\s+)?goals?",
        r"public\s+guardian\s+(?:ignores?|dismisses?)\s+(?:stated\s+)?(?:wishes?|preferences?)",
    ]

    PG_DELAY_PATTERNS = [
        r"public\s+guardian\s+(?:delays?|postpones?|stalls?)",
        r"(?:waiting|delayed)\s+(?:for|by)\s+public\s+guardian",
        r"(?:slow|lengthy|extended)\s+(?:response|approval|decision)",
        r"public\s+guardian\s+(?:bureaucracy|process|procedures?)",
        r"(?:months?|weeks?)\s+(?:to|for)\s+(?:get|receive|obtain)\s+(?:approval|response|decision)",
    ]

    @classmethod
    def extract_limitations(cls, text: str, patterns: List[str], category: str, pages: List) -> List[EvidenceItem]:
        """Extract Public Guardian limitation evidence"""
        evidence_items = []

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Get context
                start = max(0, match.start() - 150)
                end = min(len(text), match.end() + 150)
                context = text[start:end].strip()

                # Find page number
                page_num = 0
                for page in pages:
                    if match.group().lower() in page.text.lower():
                        page_num = page.page_number
                        break

                # Higher relevance for specific examples
                relevance_score = 0.7
                if re.search(r'\b(?:example|specifically|instance)\b', context, re.IGNORECASE):
                    relevance_score = 0.9
                if re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', context):
                    relevance_score = min(1.0, relevance_score + 0.1)

                evidence_items.append(EvidenceItem(
                    text=match.group(),
                    page_number=page_num,
                    category=category,
                    relevance_score=round(relevance_score, 2),
                    context=context
                ))

        return evidence_items


async def extract_public_guardian_limitations(
    request: FamilySupportEvidenceRequest  # Reusing same request model
) -> FamilySupportEvidenceResponse:  # Reusing same response model
    """
    Tool 11: Extract risks or negative impacts from Public Guardian oversight
    """
    try:
        logger.info(f"Extracting Public Guardian limitations from: {request.file_path}")

        # Extract text from PDF
        pdf_request = PDFExtractionRequest(file_path=request.file_path, extract_metadata=False)
        pdf_result = await extract_text_from_pdf(pdf_request)

        text = pdf_result.full_text
        pages = pdf_result.pages

        # Extract limitations by category
        barriers = PublicGuardianLimitationsExtractor.extract_limitations(
            text, PublicGuardianLimitationsExtractor.PG_BARRIER_PATTERNS, "barriers", pages
        )

        family_separation = PublicGuardianLimitationsExtractor.extract_limitations(
            text, PublicGuardianLimitationsExtractor.PG_FAMILY_SEPARATION_PATTERNS,
            "family_separation", pages
        )

        cultural_disconnect = PublicGuardianLimitationsExtractor.extract_limitations(
            text, PublicGuardianLimitationsExtractor.PG_CULTURAL_DISCONNECT_PATTERNS,
            "cultural_disconnect", pages
        )

        personal_knowledge = PublicGuardianLimitationsExtractor.extract_limitations(
            text, PublicGuardianLimitationsExtractor.PG_PERSONAL_KNOWLEDGE_PATTERNS,
            "personal_knowledge_gaps", pages
        )

        goal_conflicts = PublicGuardianLimitationsExtractor.extract_limitations(
            text, PublicGuardianLimitationsExtractor.PG_GOAL_CONFLICT_PATTERNS,
            "goal_conflicts", pages
        )

        delays = PublicGuardianLimitationsExtractor.extract_limitations(
            text, PublicGuardianLimitationsExtractor.PG_DELAY_PATTERNS, "delays", pages
        )

        # Combine all evidence
        all_evidence = (barriers + family_separation + cultural_disconnect +
                       personal_knowledge + goal_conflicts + delays)

        # Create themes object (reusing structure)
        themes = FamilySupportThemes(
            emotional=barriers,  # Repurposing fields
            community=family_separation,
            daily_living=cultural_disconnect,
            cultural=personal_knowledge,
            employment=goal_conflicts,
            decision_making=delays
        )

        # Generate summary
        category_counts = {
            "access barriers": len(barriers),
            "family separation": len(family_separation),
            "cultural disconnect": len(cultural_disconnect),
            "knowledge gaps": len(personal_knowledge),
            "goal conflicts": len(goal_conflicts),
            "delays": len(delays),
        }

        summary_parts = [
            f"Found {len(all_evidence)} instances of Public Guardian limitations across {len([c for c in category_counts.values() if c > 0])} categories."
        ]

        if category_counts:
            top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            if top_categories and top_categories[0][1] > 0:
                summary_parts.append(
                    f"Primary concerns: {', '.join([f'{cat} ({count})' for cat, count in top_categories if count > 0])}."
                )

        summary = " ".join(summary_parts)

        logger.info(f"Extracted {len(all_evidence)} Public Guardian limitation instances")

        return FamilySupportEvidenceResponse(
            file_path=request.file_path,
            family_support_instances=all_evidence,
            themes=themes,
            total_instances=len(all_evidence),
            summary=summary
        )

    except Exception as e:
        logger.error(f"Error extracting Public Guardian limitations: {str(e)}")
        raise
