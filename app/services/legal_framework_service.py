"""
Legal Framework Analysis Service
Tools 16-19: Human rights breaches, guardianship risk assessment, state bias, professional compliance
"""

from typing import List, Dict, Optional
import re
from datetime import datetime

from app.models.legal import (
    HumanRightsBreachRequest,
    HumanRightsBreachResponse,
    HumanRightsBreach,
    GuardianshipRiskRequest,
    GuardianshipRiskResponse,
    GuardianshipRiskAssessment,
    StateGuardianshipBiasRequest,
    StateGuardianshipBiasResponse,
    ProfessionalComplianceRequest,
    ProfessionalComplianceResponse,
)
from app.services.pdf_service import extract_text_from_pdf


class HumanRightsAnalyzer:
    """
    Analyzes documents for human rights breaches under:
    - Human Rights Act 2019 (Qld)
    - Guardianship and Administration Act 2000 (Qld)
    - UN Convention on Rights of Persons with Disabilities
    """

    # Human Rights Act 2019 (Qld) - Key Rights
    RIGHTS_PATTERNS = {
        "privacy_and_reputation": {
            "section": "Section 25",
            "patterns": [
                r"shar(?:e|ing|ed)\s+(?:private|personal|confidential)\s+information",
                r"disclos(?:e|ing|ed)\s+(?:without|no)\s+(?:consent|permission)",
                r"breach(?:ed|ing)?\s+(?:of\s+)?(?:privacy|confidentiality)",
                r"inappropriately\s+shar(?:e|ed|ing)",
                r"unauthori[sz]ed\s+(?:access|disclosure|sharing)",
                r"violat(?:e|ed|ing)\s+(?:privacy|confidentiality)",
            ],
            "weight": 0.9,
        },
        "protection_of_families_and_children": {
            "section": "Section 26",
            "patterns": [
                r"separat(?:e|ed|ing)\s+(?:from\s+)?family",
                r"restrict(?:ed|ing)?\s+(?:family\s+)?(?:contact|access|visits?)",
                r"limit(?:ed|ing)?\s+(?:family\s+)?(?:involvement|participation)",
                r"remov(?:e|ed|ing)\s+from\s+family",
                r"prevent(?:ed|ing)?\s+family\s+(?:contact|visits?|involvement)",
                r"barr(?:ed|ing)?\s+family\s+(?:access|contact)",
                r"no\s+family\s+(?:contact|access|involvement)",
            ],
            "weight": 1.0,
        },
        "cultural_rights": {
            "section": "Section 28",
            "patterns": [
                r"(?:ignor|dismiss)(?:e|ed|ing)\s+(?:cultural|traditional)\s+(?:practices?|beliefs?|values?)",
                r"lack(?:s|ing)?\s+(?:of\s+)?cultural\s+(?:understanding|awareness|sensitivity)",
                r"(?:no|without)\s+cultural\s+(?:consideration|respect|understanding)",
                r"cultural(?:ly)?\s+(?:inappropriate|insensitive|unaware)",
                r"fail(?:ed|ing|ure)?\s+to\s+(?:respect|understand|consider)\s+culture",
                r"(?:Indigenous|Aboriginal|Torres\s+Strait|CALD)\s+(?:culture|traditions?|practices?)\s+(?:ignored|dismissed)",
            ],
            "weight": 0.95,
        },
        "freedom_of_expression": {
            "section": "Section 21",
            "patterns": [
                r"silenc(?:e|ed|ing)\s+(?:the\s+)?(?:client|person)",
                r"not\s+(?:allowed|permitted)\s+to\s+(?:speak|express|voice)",
                r"prevent(?:ed|ing)?\s+from\s+(?:speaking|expressing)",
                r"(?:ignor|dismiss)(?:e|ed|ing)\s+(?:client\'?s?|person\'?s?)\s+(?:views?|opinions?|wishes)",
                r"no\s+voice\s+in\s+(?:decisions?|matters?)",
                r"opinion(?:s)?\s+(?:not|never)\s+(?:sought|considered|heard)",
            ],
            "weight": 0.85,
        },
        "freedom_of_movement": {
            "section": "Section 19",
            "patterns": [
                r"restrict(?:ed|ing|ion)?\s+(?:movement|mobility|travel)",
                r"confin(?:e|ed|ing|ement)\s+to",
                r"not\s+(?:allowed|permitted)\s+to\s+(?:leave|go|travel)",
                r"prevent(?:ed|ing)?\s+from\s+(?:leaving|going|traveling)",
                r"lock(?:ed)?\s+in",
                r"(?:cannot|can\'?t)\s+(?:leave|go\s+out)",
            ],
            "weight": 0.85,
        },
        "right_to_liberty": {
            "section": "Section 29",
            "patterns": [
                r"(?:involuntary|forced)\s+(?:placement|admission|confinement)",
                r"against\s+(?:their|his|her)\s+will",
                r"(?:no|without)\s+consent",
                r"detain(?:ed|ing|ment)",
                r"held\s+(?:involuntarily|against\s+will)",
            ],
            "weight": 0.95,
        },
    }

    @classmethod
    async def analyze_human_rights_breaches(
        cls, request: HumanRightsBreachRequest
    ) -> HumanRightsBreachResponse:
        """Analyze document for human rights breaches"""

        # Extract text
        extraction_result = await extract_text_from_pdf({"file_path": request.file_path})
        full_text = extraction_result["full_text"]

        breaches: List[HumanRightsBreach] = []

        # Analyze each rights category
        for category, config in cls.RIGHTS_PATTERNS.items():
            for pattern in config["patterns"]:
                matches = re.finditer(pattern, full_text, re.IGNORECASE)

                for match in matches:
                    # Extract context
                    start = max(0, match.start() - 150)
                    end = min(len(full_text), match.end() + 150)
                    context = full_text[start:end].strip()

                    # Find page number
                    page = cls._find_page_number(full_text, match.start(), extraction_result.get("pages", []))

                    breach = HumanRightsBreach(
                        right_category=category.replace("_", " ").title(),
                        legislation_section=config["section"],
                        breach_description=match.group(0),
                        context=context,
                        severity="high" if config["weight"] >= 0.9 else "medium",
                        page_number=page,
                        legal_basis=cls._get_legal_basis(category),
                    )
                    breaches.append(breach)

        # Calculate overall risk score
        total_breaches = len(breaches)
        high_severity = sum(1 for b in breaches if b.severity == "high")
        risk_score = min(10.0, (total_breaches * 0.5) + (high_severity * 1.5))

        # Generate narrative
        narrative = cls._generate_breach_narrative(breaches, risk_score)

        return HumanRightsBreachResponse(
            breaches=breaches,
            total_breaches=total_breaches,
            risk_score=round(risk_score, 1),
            analysis_summary=narrative,
        )

    @staticmethod
    def _find_page_number(full_text: str, position: int, pages: List[Dict]) -> Optional[int]:
        """Find page number for a text position"""
        if not pages:
            return None

        char_count = 0
        for page in pages:
            page_text = page.get("text", "")
            char_count += len(page_text)
            if char_count >= position:
                return page.get("page_number", 1)

        return len(pages)

    @staticmethod
    def _get_legal_basis(category: str) -> str:
        """Get legal basis for each rights category"""
        legal_bases = {
            "privacy_and_reputation": "Human Rights Act 2019 (Qld) s.25 - Every person has the right to privacy and reputation",
            "protection_of_families_and_children": "Human Rights Act 2019 (Qld) s.26 - Families are entitled to protection",
            "cultural_rights": "Human Rights Act 2019 (Qld) s.28 - Aboriginal and Torres Strait Islander peoples hold distinct cultural rights",
            "freedom_of_expression": "Human Rights Act 2019 (Qld) s.21 - Every person has the right to freedom of expression",
            "freedom_of_movement": "Human Rights Act 2019 (Qld) s.19 - Every person has the right to freedom of movement",
            "right_to_liberty": "Human Rights Act 2019 (Qld) s.29 - Every person has the right to liberty and security",
        }
        return legal_bases.get(category, "Human Rights Act 2019 (Qld)")

    @staticmethod
    def _generate_breach_narrative(breaches: List[HumanRightsBreach], risk_score: float) -> str:
        """Generate narrative summary of breaches"""
        if not breaches:
            return "No significant human rights breaches identified in this document."

        # Group by category
        by_category = {}
        for breach in breaches:
            category = breach.right_category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(breach)

        narrative_parts = [
            f"Human Rights Analysis identified {len(breaches)} potential breaches across {len(by_category)} rights categories (Risk Score: {risk_score}/10).\n"
        ]

        for category, category_breaches in by_category.items():
            high_severity = sum(1 for b in category_breaches if b.severity == "high")
            narrative_parts.append(
                f"\n{category} ({len(category_breaches)} instances, {high_severity} high severity):"
            )
            narrative_parts.append(f"- Legal Basis: {category_breaches[0].legal_basis}")
            narrative_parts.append(f"- Examples found on pages: {', '.join(str(b.page_number) for b in category_breaches[:3] if b.page_number)}")

        narrative_parts.append(
            "\n\nQCAT Consideration: These breaches may support arguments under s.12 Guardianship and Administration Act 2000 (Qld) - "
            "decisions must respect the adult's will and preferences and be the least restrictive of their rights."
        )

        return "\n".join(narrative_parts)


class GuardianshipRiskAnalyzer:
    """
    Analyzes documents for guardianship risk assessment compliance
    Based on Guardianship and Administration Act 2000 (Qld) principles
    """

    RISK_FACTORS = {
        "restrictiveness": {
            "description": "Whether the proposed guardianship is the least restrictive option",
            "positive_indicators": [
                r"least\s+restrictive",
                r"minimal\s+restriction",
                r"support(?:ed)?\s+decision[- ]making",
                r"informal\s+support",
                r"maintain(?:s|ing)?\s+autonomy",
            ],
            "negative_indicators": [
                r"full\s+guardianship",
                r"all\s+(?:decisions?|matters?)",
                r"complete\s+control",
                r"no\s+decision[- ]making",
                r"remove(?:s|d)?\s+all\s+rights",
            ],
        },
        "will_and_preferences": {
            "description": "Consideration of the adult's will and preferences",
            "positive_indicators": [
                r"client\s+(?:wants|wishes|prefers|expresses)",
                r"in\s+accordance\s+with\s+(?:their|his|her)\s+wishes",
                r"respects?\s+(?:client\'?s?|their)\s+preferences?",
                r"consulted\s+(?:with\s+)?(?:client|person)",
                r"sought\s+(?:client\'?s?|their)\s+views?",
            ],
            "negative_indicators": [
                r"regardless\s+of\s+(?:their|client\'?s?)\s+(?:wishes|views|preferences)",
                r"(?:client|person)\s+(?:is\s+)?(?:unable|incapable)\s+to\s+(?:decide|express)",
                r"(?:ignor|dismiss)(?:ed|ing)?\s+(?:client\'?s?|their)\s+(?:wishes|views|preferences)",
                r"not\s+(?:capable|able)\s+(?:of|to)\s+(?:deciding|expressing)",
            ],
        },
        "family_involvement": {
            "description": "Consideration of family and support network",
            "positive_indicators": [
                r"family\s+(?:can|is\s+able|capable)",
                r"family\s+(?:provides?|supports?|assists?)",
                r"strong\s+family\s+(?:support|involvement|network)",
                r"family\s+(?:understands?|knows)",
            ],
            "negative_indicators": [
                r"family\s+(?:cannot|is\s+(?:un)?able|incapable)",
                r"family\s+(?:lacks|fails)",
                r"inadequate\s+family\s+support",
                r"family\s+(?:dysfunction|conflict)",
                r"no\s+family\s+(?:support|involvement)",
            ],
        },
        "cultural_considerations": {
            "description": "Respect for cultural background and identity",
            "positive_indicators": [
                r"cultural(?:ly)?\s+(?:appropriate|sensitive|respectful)",
                r"(?:respect|understand)(?:s|ing)?\s+cultural",
                r"cultural\s+(?:identity|background|heritage)\s+(?:maintained|supported|respected)",
            ],
            "negative_indicators": [
                r"cultural\s+(?:barrier|challenge|difficulty)",
                r"(?:no|lack\s+of)\s+cultural\s+(?:understanding|awareness)",
                r"cultural(?:ly)?\s+(?:inappropriate|insensitive)",
            ],
        },
        "evidence_quality": {
            "description": "Quality and reliability of evidence",
            "positive_indicators": [
                r"observed\s+on\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
                r"documented\s+(?:on|at)",
                r"witnessed\s+by",
                r"consistent\s+with\s+(?:previous|other|records)",
            ],
            "negative_indicators": [
                r"(?:always|never)\s+",
                r"generally\s+",
                r"(?:usually|typically)\s+",
                r"no\s+(?:specific|documented)\s+(?:evidence|examples?|dates?)",
                r"(?:believed|assumed)\s+to",
            ],
        },
    }

    @classmethod
    async def analyze_guardianship_risk(
        cls, request: GuardianshipRiskRequest
    ) -> GuardianshipRiskResponse:
        """Analyze guardianship risk assessment quality"""

        # Extract text
        extraction_result = await extract_text_from_pdf({"file_path": request.file_path})
        full_text = extraction_result["full_text"]

        assessment = GuardianshipRiskAssessment(
            restrictiveness_score=0.0,
            will_preferences_score=0.0,
            family_involvement_score=0.0,
            cultural_considerations_score=0.0,
            evidence_quality_score=0.0,
            overall_compliance_score=0.0,
            risk_factors=[],
            protective_factors=[],
            compliance_issues=[],
            recommendations=[],
        )

        # Analyze each risk factor
        for factor_name, factor_config in cls.RISK_FACTORS.items():
            positive_count = 0
            negative_count = 0

            # Count positive indicators
            for pattern in factor_config["positive_indicators"]:
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                positive_count += len(matches)

            # Count negative indicators
            for pattern in factor_config["negative_indicators"]:
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                negative_count += len(matches)

            # Calculate score (0-10, higher is better compliance)
            if positive_count + negative_count == 0:
                score = 5.0  # Neutral if no indicators
            else:
                score = (positive_count / (positive_count + negative_count)) * 10

            # Set score
            score_field = f"{factor_name}_score"
            setattr(assessment, score_field, round(score, 1))

            # Add to protective or risk factors
            if score >= 6.0:
                assessment.protective_factors.append(
                    f"{factor_config['description']}: {positive_count} positive indicators found"
                )
            else:
                assessment.risk_factors.append(
                    f"{factor_config['description']}: {negative_count} concerning indicators found"
                )

            # Add compliance issues if score is low
            if score < 5.0:
                assessment.compliance_issues.append(
                    f"Low compliance with {factor_name.replace('_', ' ')}: Score {score:.1f}/10"
                )

        # Calculate overall compliance
        assessment.overall_compliance_score = round(
            (
                assessment.restrictiveness_score
                + assessment.will_preferences_score
                + assessment.family_involvement_score
                + assessment.cultural_considerations_score
                + assessment.evidence_quality_score
            )
            / 5,
            1,
        )

        # Generate recommendations
        assessment.recommendations = cls._generate_recommendations(assessment)

        # Generate narrative
        narrative = cls._generate_risk_narrative(assessment)

        return GuardianshipRiskResponse(
            assessment=assessment,
            compliance_rating=cls._get_compliance_rating(assessment.overall_compliance_score),
            analysis_summary=narrative,
        )

    @staticmethod
    def _get_compliance_rating(score: float) -> str:
        """Get compliance rating based on score"""
        if score >= 8.0:
            return "high_compliance"
        elif score >= 6.0:
            return "moderate_compliance"
        elif score >= 4.0:
            return "low_compliance"
        else:
            return "non_compliant"

    @staticmethod
    def _generate_recommendations(assessment: GuardianshipRiskAssessment) -> List[str]:
        """Generate recommendations based on assessment"""
        recommendations = []

        if assessment.restrictiveness_score < 6.0:
            recommendations.append(
                "Consider less restrictive alternatives to guardianship, such as supported decision-making arrangements"
            )

        if assessment.will_preferences_score < 6.0:
            recommendations.append(
                "Ensure the adult's will and preferences are properly documented and considered in all decisions"
            )

        if assessment.family_involvement_score < 6.0:
            recommendations.append(
                "Properly assess family capacity and involvement before dismissing family guardianship"
            )

        if assessment.cultural_considerations_score < 6.0:
            recommendations.append(
                "Conduct culturally appropriate assessment with cultural liaison if needed"
            )

        if assessment.evidence_quality_score < 6.0:
            recommendations.append(
                "Provide specific, dated, documented evidence rather than generalizations"
            )

        if not recommendations:
            recommendations.append("Assessment demonstrates good compliance with guardianship principles")

        return recommendations

    @staticmethod
    def _generate_risk_narrative(assessment: GuardianshipRiskAssessment) -> str:
        """Generate narrative summary"""
        rating = "HIGH" if assessment.overall_compliance_score >= 7 else "MODERATE" if assessment.overall_compliance_score >= 5 else "LOW"

        narrative = [
            f"Guardianship Risk Assessment Analysis (Overall Compliance: {assessment.overall_compliance_score}/10 - {rating})\n",
            "\nCompliance Scores:",
            f"- Restrictiveness (least restrictive option): {assessment.restrictiveness_score}/10",
            f"- Will and Preferences: {assessment.will_preferences_score}/10",
            f"- Family Involvement: {assessment.family_involvement_score}/10",
            f"- Cultural Considerations: {assessment.cultural_considerations_score}/10",
            f"- Evidence Quality: {assessment.evidence_quality_score}/10",
        ]

        if assessment.risk_factors:
            narrative.append(f"\n\nRisk Factors Identified ({len(assessment.risk_factors)}):")
            for factor in assessment.risk_factors[:5]:
                narrative.append(f"- {factor}")

        if assessment.protective_factors:
            narrative.append(f"\n\nProtective Factors Identified ({len(assessment.protective_factors)}):")
            for factor in assessment.protective_factors[:5]:
                narrative.append(f"- {factor}")

        if assessment.compliance_issues:
            narrative.append(f"\n\nCompliance Issues ({len(assessment.compliance_issues)}):")
            for issue in assessment.compliance_issues:
                narrative.append(f"- {issue}")

        narrative.append(
            "\n\nQCAT Consideration: This assessment evaluates compliance with Guardianship and Administration Act 2000 (Qld) "
            "principles including least restrictive option, will and preferences, and proper evidence."
        )

        return "\n".join(narrative)


class StateGuardianshipBiasDetector:
    """
    Detects bias toward state guardianship appointment
    Identifies language favoring Public Guardian over family
    """

    BIAS_PATTERNS = {
        "state_preference": [
            r"(?:prefer|recommend|suggest)(?:s|ed|ing)?\s+(?:Public\s+Guardian|State\s+Guardian|independent\s+guardian)",
            r"(?:Public\s+Guardian|State\s+Guardian)\s+(?:is\s+)?(?:best|better|more\s+appropriate)",
            r"family\s+(?:not|un)(?:suitable|appropriate|qualified)",
            r"(?:independent|professional)\s+guardian\s+(?:needed|required|necessary)",
        ],
        "family_dismissal": [
            r"family\s+(?:cannot|is\s+unable|lacks\s+capacity)",
            r"family\s+(?:conflict|dysfunction|inadequate)",
            r"concerns?\s+(?:about|with|regarding)\s+family",
            r"family\s+(?:not|in)capable",
            r"family\s+(?:fails?|failed)\s+to",
        ],
        "state_idealization": [
            r"(?:Public\s+Guardian|State)\s+(?:will|can)\s+(?:provide|ensure|protect)",
            r"(?:independent|professional|impartial)\s+(?:oversight|management|protection)",
            r"(?:Public\s+Guardian|State)\s+(?:experience|expertise|training)",
        ],
        "unsupported_claims": [
            r"family\s+(?:always|never|consistently)\s+",
            r"(?:Public\s+Guardian|State)\s+(?:always|consistently)\s+",
            r"(?:generally|typically|usually)\s+(?:family|families)",
        ],
    }

    @classmethod
    async def detect_state_guardianship_bias(
        cls, request: StateGuardianshipBiasRequest
    ) -> StateGuardianshipBiasResponse:
        """Detect bias toward state guardianship"""

        # Extract text
        extraction_result = await extract_text_from_pdf({"file_path": request.file_path})
        full_text = extraction_result["full_text"]

        bias_indicators = []
        bias_score = 0.0

        # Analyze each bias pattern category
        for category, patterns in cls.BIAS_PATTERNS.items():
            category_matches = 0

            for pattern in patterns:
                matches = re.finditer(pattern, full_text, re.IGNORECASE)

                for match in matches:
                    category_matches += 1

                    # Extract context
                    start = max(0, match.start() - 100)
                    end = min(len(full_text), match.end() + 100)
                    context = full_text[start:end].strip()

                    bias_indicators.append({
                        "category": category.replace("_", " ").title(),
                        "text": match.group(0),
                        "context": context,
                        "concern_level": "high" if category in ["state_preference", "family_dismissal"] else "medium",
                    })

            # Add to bias score
            if category in ["state_preference", "family_dismissal"]:
                bias_score += category_matches * 0.8
            else:
                bias_score += category_matches * 0.5

        # Calculate final bias score (0-10)
        bias_score = min(10.0, bias_score)

        # Determine bias level
        if bias_score >= 7.0:
            bias_level = "high"
        elif bias_score >= 4.0:
            bias_level = "moderate"
        else:
            bias_level = "low"

        # Generate narrative
        narrative = cls._generate_bias_narrative(bias_indicators, bias_score, bias_level)

        return StateGuardianshipBiasResponse(
            bias_indicators=bias_indicators,
            bias_score=round(bias_score, 1),
            bias_level=bias_level,
            total_indicators=len(bias_indicators),
            analysis_summary=narrative,
        )

    @staticmethod
    def _generate_bias_narrative(bias_indicators: List[Dict], bias_score: float, bias_level: str) -> str:
        """Generate narrative summary of bias"""
        if not bias_indicators:
            return "No significant bias toward state guardianship detected. Assessment appears balanced."

        # Group by category
        by_category = {}
        for indicator in bias_indicators:
            category = indicator["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(indicator)

        narrative = [
            f"State Guardianship Bias Analysis (Bias Score: {bias_score}/10 - {bias_level.upper()} bias detected)\n",
            f"\nIdentified {len(bias_indicators)} bias indicators across {len(by_category)} categories:\n",
        ]

        for category, indicators in by_category.items():
            high_concern = sum(1 for i in indicators if i.get("concern_level") == "high")
            narrative.append(f"\n{category}: {len(indicators)} instances ({high_concern} high concern)")
            narrative.append(f"Examples:")
            for indicator in indicators[:2]:
                narrative.append(f'- "{indicator["text"]}"')

        narrative.append(
            "\n\nQCAT Consideration: This bias analysis may support arguments that the assessment lacks objectivity "
            "and fails to properly consider family guardianship as a viable alternative per s.12 principles."
        )

        return "\n".join(narrative)


class ProfessionalLanguageAnalyzer:
    """
    Analyzes professional language compliance
    Identifies non-person-centered, stigmatizing, or unprofessional language
    """

    COMPLIANCE_ISSUES = {
        "deficit_language": {
            "description": "Deficit-focused rather than strength-based language",
            "patterns": [
                r"\b(?:cannot|can\'?t|unable|incapable|fails?|failed)\b",
                r"\b(?:lacks?|lacking|deficit|deficient)\b",
                r"\b(?:poor|inadequate|insufficient|limited)\b",
                r"\b(?:problem|issue|concern|difficulty)\b",
            ],
            "severity": "medium",
        },
        "medical_model": {
            "description": "Medical model rather than social model of disability",
            "patterns": [
                r"(?:suffering|suffers)\s+from",
                r"afflicted\s+(?:with|by)",
                r"victim\s+of",
                r"confined\s+to",
                r"bound\s+to",
            ],
            "severity": "high",
        },
        "labels_not_people": {
            "description": "Labels used instead of person-first language",
            "patterns": [
                r"\b(?:the\s+)?(?:disabled|handicapped|retarded|mentally\s+ill)\b",
                r"\b(?:the\s+)?(?:autistic|schizophrenic|bipolar)\b",
                r"\bwheelchair\s+bound\b",
                r"\b(?:high|low)\s+functioning\b",
            ],
            "severity": "high",
        },
        "judgmental_language": {
            "description": "Judgmental or stigmatizing language",
            "patterns": [
                r"\b(?:difficult|challenging|non[- ]compliant|uncooperative)\s+(?:client|patient|person)\b",
                r"\b(?:refuses?|refusing|refused)\s+to\b",
                r"\b(?:manipulative|attention[- ]seeking|demanding)\b",
                r"\bfails?\s+to\s+(?:comply|cooperate|engage)\b",
            ],
            "severity": "high",
        },
        "unsupported_generalizations": {
            "description": "Generalizations without evidence",
            "patterns": [
                r"\b(?:always|never|constantly|consistently)\s+",
                r"\b(?:all\s+the\s+time|every\s+time)\b",
                r"\b(?:generally|typically|usually|often)\b",
                r"\btends?\s+to\b",
            ],
            "severity": "medium",
        },
    }

    @classmethod
    async def analyze_professional_compliance(
        cls, request: ProfessionalComplianceRequest
    ) -> ProfessionalComplianceResponse:
        """Analyze professional language compliance"""

        # Extract text
        extraction_result = await extract_text_from_pdf({"file_path": request.file_path})
        full_text = extraction_result["full_text"]

        compliance_issues = []
        total_score = 0.0

        # Analyze each compliance category
        for category, config in cls.COMPLIANCE_ISSUES.items():
            category_issues = 0

            for pattern in config["patterns"]:
                matches = re.finditer(pattern, full_text, re.IGNORECASE)

                for match in matches:
                    category_issues += 1

                    # Extract context
                    start = max(0, match.start() - 100)
                    end = min(len(full_text), match.end() + 100)
                    context = full_text[start:end].strip()

                    compliance_issues.append({
                        "category": category.replace("_", " ").title(),
                        "issue": match.group(0),
                        "context": context,
                        "severity": config["severity"],
                        "description": config["description"],
                    })

            # Add to score (higher issue count = lower compliance)
            if config["severity"] == "high":
                total_score += category_issues * 1.5
            else:
                total_score += category_issues * 0.8

        # Calculate compliance score (10 = perfect, 0 = many issues)
        compliance_score = max(0.0, 10.0 - min(10.0, total_score * 0.1))

        # Determine compliance level
        if compliance_score >= 8.0:
            compliance_level = "high"
        elif compliance_score >= 5.0:
            compliance_level = "moderate"
        else:
            compliance_level = "low"

        # Generate recommendations
        recommendations = cls._generate_recommendations(compliance_issues)

        # Generate narrative
        narrative = cls._generate_compliance_narrative(
            compliance_issues, compliance_score, compliance_level
        )

        return ProfessionalComplianceResponse(
            compliance_issues=compliance_issues,
            compliance_score=round(compliance_score, 1),
            compliance_level=compliance_level,
            total_issues=len(compliance_issues),
            recommendations=recommendations,
            analysis_summary=narrative,
        )

    @staticmethod
    def _generate_recommendations(compliance_issues: List[Dict]) -> List[str]:
        """Generate recommendations based on compliance issues"""
        recommendations = []

        # Group by category
        by_category = {}
        for issue in compliance_issues:
            category = issue["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(issue)

        if "Deficit Language" in by_category:
            recommendations.append(
                "Use strength-based language focusing on abilities rather than deficits"
            )

        if "Medical Model" in by_category:
            recommendations.append(
                "Adopt social model of disability - focus on environmental barriers, not 'suffering'"
            )

        if "Labels Not People" in by_category:
            recommendations.append(
                "Use person-first language (e.g., 'person with disability' not 'disabled person')"
            )

        if "Judgmental Language" in by_category:
            recommendations.append(
                "Replace judgmental terms with objective, neutral descriptions"
            )

        if "Unsupported Generalizations" in by_category:
            recommendations.append(
                "Provide specific, dated, documented examples rather than generalizations"
            )

        if not recommendations:
            recommendations.append("Language demonstrates good professional compliance")

        return recommendations

    @staticmethod
    def _generate_compliance_narrative(
        compliance_issues: List[Dict], compliance_score: float, compliance_level: str
    ) -> str:
        """Generate narrative summary"""
        if not compliance_issues:
            return "Professional language analysis: High compliance. Language is appropriate, person-centered, and professional."

        # Group by severity
        high_severity = [i for i in compliance_issues if i["severity"] == "high"]
        medium_severity = [i for i in compliance_issues if i["severity"] == "medium"]

        narrative = [
            f"Professional Language Compliance Analysis (Score: {compliance_score}/10 - {compliance_level.upper()} compliance)\n",
            f"\nIdentified {len(compliance_issues)} compliance issues:",
            f"- High Severity: {len(high_severity)}",
            f"- Medium Severity: {len(medium_severity)}\n",
        ]

        # Group by category
        by_category = {}
        for issue in compliance_issues:
            category = issue["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(issue)

        for category, issues in by_category.items():
            narrative.append(f"\n{category}: {len(issues)} instances")
            narrative.append(f"- {issues[0]['description']}")
            narrative.append(f'- Examples: "{issues[0]["issue"]}"')

        narrative.append(
            "\n\nQCAT Consideration: Non-compliant professional language may indicate bias, lack of training, "
            "or failure to meet professional standards, undermining the credibility of the assessment."
        )

        return "\n".join(narrative)


# Main service functions

async def extract_human_rights_breaches(
    request: HumanRightsBreachRequest,
) -> HumanRightsBreachResponse:
    """Tool 16: Extract human rights breaches"""
    return await HumanRightsAnalyzer.analyze_human_rights_breaches(request)


async def analyze_guardianship_risk(
    request: GuardianshipRiskRequest,
) -> GuardianshipRiskResponse:
    """Tool 17: Analyze guardianship risk assessment"""
    return await GuardianshipRiskAnalyzer.analyze_guardianship_risk(request)


async def detect_state_guardianship_bias(
    request: StateGuardianshipBiasRequest,
) -> StateGuardianshipBiasResponse:
    """Tool 18: Detect bias toward state guardianship"""
    return await StateGuardianshipBiasDetector.detect_state_guardianship_bias(request)


async def analyze_professional_compliance(
    request: ProfessionalComplianceRequest,
) -> ProfessionalComplianceResponse:
    """Tool 19: Analyze professional language compliance"""
    return await ProfessionalLanguageAnalyzer.analyze_professional_compliance(request)
