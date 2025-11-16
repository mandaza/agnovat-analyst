"""
NDIS Goals Alignment Service
Tool 20: Analyze NDIS goals alignment with guardianship options (CRITICAL)
"""

from typing import List, Dict, Optional
import re
from datetime import datetime

from app.models.legal import (
    GoalsAlignmentRequest,
    GoalsAlignmentResponse,
    NDISGoal,
)
from app.models.pdf import PDFExtractionRequest
from app.services.pdf_service import extract_text_from_pdf


class NDISGoalsAnalyzer:
    """
    Analyzes NDIS plan goals (G1-G7) and determines which guardianship option
    (family vs Public Guardian) better aligns with client outcomes.

    CRITICAL for QCAT appeals - demonstrates evidence-based guardianship recommendation.
    """

    # NDIS Goals Framework (G1-G7)
    NDIS_GOALS = {
        "G1": {
            "name": "More Choice and Control",
            "description": "People with disability have more choice and control over their lives",
            "keywords": [
                "choice", "control", "autonomy", "independence", "self-determination",
                "decision", "preference", "wishes", "own decisions", "say in"
            ],
            "family_positive": [
                r"family\s+(?:supports?|respects?|enables?)\s+(?:choice|control|decisions?|preferences?|wishes)",
                r"(?:consults?|asks?)\s+(?:client|person)\s+(?:about|regarding)\s+(?:their\s+)?(?:wishes|preferences?|choices?)",
                r"client\s+(?:makes?|has)\s+(?:own|their)\s+(?:choice|decision)s?\s+with\s+family\s+support",
                r"family\s+(?:encourages?|promotes?)\s+(?:independence|autonomy|self-determination)",
                r"respects?\s+(?:client\'?s?|their)\s+(?:wishes|preferences?|choices?)",
            ],
            "family_negative": [
                r"family\s+(?:makes?|controls?|decides?)\s+(?:all|every|most)\s+(?:decisions?|choices?)",
                r"client\s+(?:has\s+)?no\s+(?:choice|control|say|input)",
                r"family\s+(?:overrides?|ignores?|dismisses?)\s+(?:wishes|preferences?|choices?)",
            ],
            "pg_positive": [
                r"(?:Public\s+Guardian|PG)\s+(?:respects?|supports?|enables?)\s+(?:choice|control|wishes)",
                r"(?:independent|impartial)\s+(?:support|assistance)\s+for\s+decision[- ]making",
            ],
            "pg_negative": [
                r"(?:Public\s+Guardian|PG|State|independent\s+guardian)\s+(?:makes?|decides?|controls?)",
                r"(?:Public\s+Guardian|PG)\s+(?:limited|no|minimal)\s+(?:contact|involvement|knowledge)",
                r"bureaucratic\s+(?:process|procedures?|delays?)",
                r"(?:Public\s+Guardian|PG)\s+(?:unfamiliar|doesn\'?t\s+know|doesn\'?t\s+understand)",
            ],
        },
        "G2": {
            "name": "Community Participation",
            "description": "People with disability are included in their community",
            "keywords": [
                "community", "participate", "inclusion", "social", "belong",
                "involvement", "connected", "engaged", "activities"
            ],
            "family_positive": [
                r"family\s+(?:facilitates?|supports?|enables?|arranges?)\s+(?:community|social)\s+(?:participation|involvement|activities?|connections?)",
                r"family\s+(?:takes?|brings?|accompanies?)\s+(?:to|for)\s+(?:community|social)\s+(?:events?|activities?|gatherings?)",
                r"(?:maintains?|has|continues?)\s+(?:community|social|cultural)\s+(?:connections?|ties|relationships?)\s+(?:with|through)\s+family",
                r"family\s+(?:introduces?|connects?)\s+to\s+(?:community|social|cultural)\s+(?:groups?|activities?|networks?)",
            ],
            "family_negative": [
                r"family\s+(?:isolates?|separates?|restricts?|prevents?)\s+(?:from\s+)?(?:community|social)",
                r"(?:no|limited|minimal)\s+(?:community|social)\s+(?:participation|involvement|connections?)\s+(?:with|through)\s+family",
            ],
            "pg_positive": [
                r"(?:Public\s+Guardian|PG)\s+(?:arranges?|facilitates?|supports?)\s+(?:community|social)\s+participation",
            ],
            "pg_negative": [
                r"(?:Public\s+Guardian|PG)\s+(?:limited|no|minimal)\s+(?:capacity|ability|resources?)\s+(?:for|to\s+support)\s+(?:community|social)",
                r"(?:Public\s+Guardian|PG)\s+(?:unfamiliar|doesn\'?t\s+know)\s+(?:with|about)\s+(?:community|cultural|local)",
                r"lack(?:s|ing)?\s+(?:of\s+)?(?:community|cultural|local)\s+(?:knowledge|connections?|understanding)",
            ],
        },
        "G3": {
            "name": "Employment Support",
            "description": "People with disability achieve their employment goals",
            "keywords": [
                "employment", "work", "job", "career", "occupation",
                "employment support", "workplace", "vocational"
            ],
            "family_positive": [
                r"family\s+(?:supports?|helps?|assists?|encourages?)\s+(?:with\s+)?(?:employment|work|job|career)",
                r"family\s+(?:provides?|arranges?|facilitates?)\s+(?:transport|assistance)\s+(?:to|for)\s+work",
                r"family\s+(?:runs?|operates?|manages?)\s+(?:business|enterprise)\s+(?:where|that)\s+(?:client|person)\s+(?:works?|is\s+employed)",
                r"family\s+(?:employs?|provides?\s+work|gives?\s+job)\s+to",
            ],
            "family_negative": [
                r"family\s+(?:prevents?|discourages?|blocks?|opposes?)\s+(?:employment|work|job)",
            ],
            "pg_positive": [
                r"(?:Public\s+Guardian|PG)\s+(?:supports?|assists?|facilitates?)\s+employment",
            ],
            "pg_negative": [
                r"(?:Public\s+Guardian|PG)\s+(?:no|limited|minimal)\s+(?:capacity|ability|resources?)\s+(?:for|to\s+support)\s+employment",
                r"(?:Public\s+Guardian|PG)\s+(?:unfamiliar|doesn\'?t\s+know|doesn\'?t\s+understand)\s+(?:employment|work|job)",
            ],
        },
        "G4": {
            "name": "Daily Living Skills",
            "description": "People with disability develop and maintain daily living skills",
            "keywords": [
                "daily living", "ADL", "personal care", "hygiene", "meals",
                "cooking", "cleaning", "self-care", "independent living"
            ],
            "family_positive": [
                r"family\s+(?:supports?|helps?|assists?|teaches?|encourages?)\s+(?:with\s+)?(?:daily\s+living|ADL|personal\s+care|self-care)",
                r"family\s+(?:provides?|prepares?|arranges?)\s+(?:meals?|food|cooking)",
                r"family\s+(?:assists?|helps?)\s+(?:with\s+)?(?:hygiene|bathing|showering|grooming|dressing)",
                r"family\s+(?:provides?|arranges?)\s+(?:transport|transportation|lifts?|rides?)",
                r"family\s+(?:helps?|assists?)\s+(?:with\s+)?(?:medication|health\s+management|appointments?)",
            ],
            "family_negative": [
                r"family\s+(?:does\s+everything|does\s+it\s+all|takes\s+over)",
                r"family\s+(?:doesn\'?t\s+support|fails\s+to\s+support|doesn\'?t\s+help)\s+(?:daily\s+living|ADL)",
            ],
            "pg_positive": [
                r"(?:Public\s+Guardian|PG)\s+(?:arranges?|coordinates?)\s+(?:daily\s+living|ADL)\s+support",
            ],
            "pg_negative": [
                r"(?:Public\s+Guardian|PG)\s+(?:does\s+not|doesn\'?t|cannot)\s+(?:provide|arrange|facilitate)\s+(?:daily|practical|hands-on)\s+(?:support|assistance)",
                r"(?:Public\s+Guardian|PG)\s+(?:no|limited|minimal)\s+(?:capacity|ability|involvement)\s+(?:in|with)\s+(?:daily|day-to-day)",
            ],
        },
        "G5": {
            "name": "Health and Wellbeing",
            "description": "People with disability achieve health and wellbeing goals",
            "keywords": [
                "health", "wellbeing", "medical", "healthcare", "wellness",
                "physical health", "mental health", "emotional wellbeing"
            ],
            "family_positive": [
                r"family\s+(?:supports?|monitors?|manages?|coordinates?)\s+(?:health|medical|healthcare|wellbeing)",
                r"family\s+(?:takes?|accompanies?)\s+to\s+(?:appointments?|doctor|hospital|medical)",
                r"family\s+(?:monitors?|manages?|administers?)\s+medication",
                r"family\s+(?:advocates?|speaks\s+up)\s+for\s+(?:health|medical)\s+(?:needs?|care)",
                r"family\s+(?:ensures?|makes\s+sure)\s+(?:health|medical)\s+(?:needs?|care|treatment)\s+(?:met|provided)",
            ],
            "family_negative": [
                r"family\s+(?:neglects?|ignores?|fails\s+to\s+(?:address|manage))\s+(?:health|medical)",
            ],
            "pg_positive": [
                r"(?:Public\s+Guardian|PG)\s+(?:coordinates?|manages?)\s+(?:health|medical)\s+care",
            ],
            "pg_negative": [
                r"(?:Public\s+Guardian|PG)\s+(?:limited|no|minimal)\s+(?:knowledge|understanding)\s+(?:of|about)\s+(?:health|medical)\s+(?:history|needs?|conditions?)",
                r"(?:Public\s+Guardian|PG)\s+(?:rarely|seldom|doesn\'?t)\s+(?:visit|see|meet\s+with)",
                r"delay(?:s|ed)?\s+(?:in|with)\s+(?:health|medical)\s+(?:decisions?|approvals?|consents?)",
            ],
        },
        "G6": {
            "name": "Lifelong Learning",
            "description": "People with disability achieve learning and development goals",
            "keywords": [
                "learning", "education", "training", "development", "skills",
                "courses", "programs", "study", "school"
            ],
            "family_positive": [
                r"family\s+(?:supports?|encourages?|facilitates?)\s+(?:learning|education|training|development)",
                r"family\s+(?:enrolls?|signs\s+up|registers?)\s+(?:in|for)\s+(?:courses?|programs?|training|education)",
                r"family\s+(?:helps?|assists?)\s+(?:with\s+)?(?:learning|study|education|training)",
            ],
            "family_negative": [
                r"family\s+(?:prevents?|discourages?|blocks?)\s+(?:learning|education|training)",
            ],
            "pg_positive": [
                r"(?:Public\s+Guardian|PG)\s+(?:supports?|facilitates?|arranges?)\s+(?:learning|education|training)",
            ],
            "pg_negative": [
                r"(?:Public\s+Guardian|PG)\s+(?:no|limited|minimal)\s+(?:capacity|involvement)\s+(?:in|with)\s+(?:learning|education|training)",
            ],
        },
        "G7": {
            "name": "Social, Community and Civic Participation",
            "description": "People with disability participate in social, community and civic life",
            "keywords": [
                "social", "community", "civic", "participation", "involvement",
                "cultural", "religious", "political", "volunteer"
            ],
            "family_positive": [
                r"family\s+(?:supports?|facilitates?|enables?)\s+(?:social|community|cultural|civic|religious)\s+(?:participation|involvement|activities?)",
                r"family\s+(?:takes?|brings?)\s+to\s+(?:church|temple|mosque|cultural\s+events?|community\s+gatherings?)",
                r"family\s+(?:maintains?|preserves?|supports?)\s+(?:cultural|religious|community)\s+(?:identity|connections?|traditions?|practices?)",
                r"(?:attends?|participates?\s+in)\s+(?:cultural|religious|community)\s+(?:events?|activities?|gatherings?)\s+with\s+family",
            ],
            "family_negative": [
                r"family\s+(?:restricts?|prevents?|limits?)\s+(?:social|community|cultural|civic)\s+participation",
            ],
            "pg_positive": [
                r"(?:Public\s+Guardian|PG)\s+(?:supports?|facilitates?)\s+(?:social|community|cultural|civic)\s+participation",
            ],
            "pg_negative": [
                r"(?:Public\s+Guardian|PG)\s+(?:no|limited|minimal)\s+(?:capacity|understanding|involvement)\s+(?:in|with)\s+(?:cultural|religious|community)",
                r"(?:Public\s+Guardian|PG)\s+(?:not\s+familiar|unfamiliar|doesn\'?t\s+understand)\s+(?:with\s+)?(?:cultural|religious)\s+(?:background|traditions?|practices?)",
                r"lack(?:s|ing)?\s+(?:of\s+)?(?:cultural|religious)\s+(?:understanding|sensitivity|awareness)",
            ],
        },
    }

    @classmethod
    async def analyze_goals_alignment(
        cls, request: GoalsAlignmentRequest
    ) -> GoalsAlignmentResponse:
        """
        Analyze NDIS goals alignment with guardianship options.
        CRITICAL TOOL for QCAT appeals.
        """

        # Extract text from NDIS plan
        pdf_request = PDFExtractionRequest(file_path=request.file_path)
        extraction_result = await extract_text_from_pdf(pdf_request)
        full_text = extraction_result.full_text

        goals_analysis: List[NDISGoal] = []
        total_family_score = 0.0
        total_pg_score = 0.0

        # Analyze each NDIS goal (G1-G7)
        for goal_num, goal_config in cls.NDIS_GOALS.items():
            goal_analysis = await cls._analyze_single_goal(
                goal_num, goal_config, full_text, request.guardianship_context
            )
            goals_analysis.append(goal_analysis)
            total_family_score += goal_analysis.family_alignment_score
            total_pg_score += goal_analysis.pg_alignment_score

        # Calculate overall scores
        num_goals = len(cls.NDIS_GOALS)
        overall_family_alignment = round(total_family_score / num_goals, 1)
        overall_pg_alignment = round(total_pg_score / num_goals, 1)
        alignment_differential = round(overall_family_alignment - overall_pg_alignment, 1)

        # Generate recommendation
        recommendation = cls._generate_recommendation(
            overall_family_alignment, overall_pg_alignment, alignment_differential
        )

        # Generate QCAT argument
        qcat_argument = cls._generate_qcat_argument(
            goals_analysis, overall_family_alignment, overall_pg_alignment, alignment_differential
        )

        # Generate summary
        analysis_summary = cls._generate_summary(
            goals_analysis, overall_family_alignment, overall_pg_alignment, alignment_differential
        )

        return GoalsAlignmentResponse(
            goals_analysis=goals_analysis,
            overall_family_alignment=overall_family_alignment,
            overall_pg_alignment=overall_pg_alignment,
            alignment_differential=alignment_differential,
            recommendation=recommendation,
            qcat_argument=qcat_argument,
            analysis_summary=analysis_summary,
        )

    @classmethod
    async def _analyze_single_goal(
        cls, goal_num: str, goal_config: Dict, text: str, context: Optional[str]
    ) -> NDISGoal:
        """Analyze alignment for a single NDIS goal"""

        # Count family positive indicators
        family_positive_count = 0
        family_positive_evidence = []
        for pattern in goal_config["family_positive"]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                family_positive_count += 1
                # Extract context
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                evidence = text[start:end].strip()
                family_positive_evidence.append(f'"{match.group(0)}" - {evidence[:80]}...')

        # Count family negative indicators
        family_negative_count = 0
        for pattern in goal_config["family_negative"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            family_negative_count += len(matches)

        # Count PG positive indicators
        pg_positive_count = 0
        pg_positive_evidence = []
        for pattern in goal_config["pg_positive"]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                pg_positive_count += 1
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                evidence = text[start:end].strip()
                pg_positive_evidence.append(f'"{match.group(0)}" - {evidence[:80]}...')

        # Count PG negative indicators
        pg_negative_count = 0
        pg_negative_evidence = []
        for pattern in goal_config["pg_negative"]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                pg_negative_count += 1
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                evidence = text[start:end].strip()
                pg_negative_evidence.append(f'"{match.group(0)}" - {evidence[:80]}...')

        # Calculate family alignment score (0-10)
        if family_positive_count + family_negative_count == 0:
            family_score = 5.0  # Neutral if no evidence
        else:
            family_score = (family_positive_count / (family_positive_count + family_negative_count)) * 10

        # Calculate PG alignment score (0-10)
        # Note: PG negative evidence LOWERS the score significantly
        if pg_positive_count + pg_negative_count == 0:
            pg_score = 5.0  # Neutral if no evidence
        else:
            # Weight negative evidence more heavily for PG (since lack of capacity is critical)
            weighted_negative = pg_negative_count * 1.5
            pg_score = max(0, (pg_positive_count / (pg_positive_count + weighted_negative)) * 10)

        # Generate analysis narrative
        analysis = cls._generate_goal_analysis(
            goal_num,
            goal_config,
            family_positive_count,
            family_negative_count,
            pg_positive_count,
            pg_negative_count,
            family_score,
            pg_score,
        )

        return NDISGoal(
            goal_number=goal_num,
            goal_name=goal_config["name"],
            goal_description=goal_config["description"],
            family_alignment_score=round(family_score, 1),
            pg_alignment_score=round(pg_score, 1),
            evidence_for_family=family_positive_evidence[:5],  # Top 5
            evidence_against_pg=pg_negative_evidence[:5],  # Top 5
            analysis=analysis,
        )

    @staticmethod
    def _generate_goal_analysis(
        goal_num: str,
        goal_config: Dict,
        family_pos: int,
        family_neg: int,
        pg_pos: int,
        pg_neg: int,
        family_score: float,
        pg_score: float,
    ) -> str:
        """Generate analysis narrative for a single goal"""

        differential = family_score - pg_score

        analysis = [
            f"{goal_num}: {goal_config['name']}",
            f"Family Alignment: {family_score:.1f}/10 ({family_pos} positive, {family_neg} negative indicators)",
            f"PG Alignment: {pg_score:.1f}/10 ({pg_pos} positive, {pg_neg} negative indicators)",
            f"Differential: {differential:+.1f} ({'Family advantage' if differential > 0 else 'PG advantage' if differential < 0 else 'Neutral'})",
        ]

        if differential >= 3.0:
            analysis.append(
                f"\nSTRONG FAMILY ADVANTAGE: Evidence shows family guardianship significantly better "
                f"supports {goal_config['name']} outcomes."
            )
        elif differential >= 1.0:
            analysis.append(
                f"\nFAMILY ADVANTAGE: Evidence indicates family guardianship better aligns with "
                f"{goal_config['name']} goals."
            )
        elif differential <= -3.0:
            analysis.append(
                f"\nSTRONG PG ADVANTAGE: Evidence suggests Public Guardian better supports "
                f"{goal_config['name']} outcomes."
            )
        elif differential <= -1.0:
            analysis.append(
                f"\nPG ADVANTAGE: Evidence indicates Public Guardian better aligns with "
                f"{goal_config['name']} goals."
            )
        else:
            analysis.append(
                f"\nNEUTRAL: Evidence does not clearly favor either guardianship option for "
                f"{goal_config['name']}."
            )

        return "\n".join(analysis)

    @staticmethod
    def _generate_recommendation(
        family_score: float, pg_score: float, differential: float
    ) -> str:
        """Generate guardianship recommendation based on alignment scores"""

        if differential >= 2.0:
            return (
                f"STRONG RECOMMENDATION: Family Guardianship (Family: {family_score}/10, PG: {pg_score}/10, "
                f"Differential: {differential:+.1f}). Evidence shows family guardianship significantly "
                f"better aligns with NDIS goals and client outcomes."
            )
        elif differential >= 0.5:
            return (
                f"RECOMMENDATION: Family Guardianship (Family: {family_score}/10, PG: {pg_score}/10, "
                f"Differential: {differential:+.1f}). Evidence indicates family guardianship better "
                f"supports NDIS goals."
            )
        elif differential <= -2.0:
            return (
                f"STRONG RECOMMENDATION: Public Guardian (Family: {family_score}/10, PG: {pg_score}/10, "
                f"Differential: {differential:+.1f}). Evidence shows Public Guardian significantly "
                f"better aligns with NDIS goals."
            )
        elif differential <= -0.5:
            return (
                f"RECOMMENDATION: Public Guardian (Family: {family_score}/10, PG: {pg_score}/10, "
                f"Differential: {differential:+.1f}). Evidence indicates Public Guardian better "
                f"supports NDIS goals."
            )
        else:
            return (
                f"NEUTRAL: No clear preference (Family: {family_score}/10, PG: {pg_score}/10, "
                f"Differential: {differential:+.1f}). Both options show similar alignment with NDIS goals."
            )

    @staticmethod
    def _generate_qcat_argument(
        goals_analysis: List[NDISGoal],
        family_score: float,
        pg_score: float,
        differential: float,
    ) -> str:
        """Generate QCAT-ready legal argument based on goals alignment"""

        if differential >= 1.0:
            # Family advantage
            argument_parts = [
                "QCAT LEGAL ARGUMENT: NDIS Goals Alignment Supports Family Guardianship\n",
                "=" * 80,
                "\n\n1. EVIDENCE-BASED ANALYSIS",
                f"\nComprehensive analysis of the client's NDIS plan goals (G1-G7) demonstrates that "
                f"family guardianship better aligns with the client's goals and outcomes:\n",
                f"- Family Guardianship Alignment: {family_score}/10",
                f"- Public Guardian Alignment: {pg_score}/10",
                f"- Differential: {differential:+.1f} in favor of family\n",
                "\n2. GOAL-BY-GOAL ANALYSIS\n",
            ]

            # Add analysis for goals where family has advantage
            for goal in goals_analysis:
                if goal.family_alignment_score > goal.pg_alignment_score:
                    advantage = goal.family_alignment_score - goal.pg_alignment_score
                    argument_parts.append(
                        f"\n{goal.goal_number} - {goal.goal_name}:"
                    )
                    argument_parts.append(
                        f"  Family: {goal.family_alignment_score}/10, PG: {goal.pg_alignment_score}/10 "
                        f"(Family advantage: {advantage:+.1f})"
                    )
                    if goal.evidence_for_family:
                        argument_parts.append(f"  Evidence: {goal.evidence_for_family[0]}")

            argument_parts.extend([
                "\n\n3. LEGAL FRAMEWORK",
                "\nGuardianship and Administration Act 2000 (Qld) General Principles:",
                "- GP5: The adult's will and preferences should be taken into account",
                "- GP1: The guardianship should be the least restrictive of the adult's rights",
                "- GP3: The adult's existing supportive relationships should be maintained",
                "\nThe NDIS plan represents the client's goals and preferences. A guardianship decision "
                "that undermines these goals fails to properly consider the adult's will and preferences "
                "as required by GP5.",
                "\n\n4. RECOMMENDATION",
                f"\nBased on comprehensive NDIS goals analysis showing {differential:+.1f} point advantage "
                f"for family guardianship, the Tribunal should find that family guardianship better serves "
                f"the client's interests and goals as expressed in their NDIS plan.",
                "\n\n5. STATUTORY COMPLIANCE",
                "\nAppointing Public Guardian when family guardianship better aligns with NDIS goals would:",
                "- Fail to give proper weight to the adult's will and preferences (GP5)",
                "- Be more restrictive than necessary (GP1)",
                "- Undermine existing supportive family relationships (GP3)",
                "\n" + "=" * 80,
            ])

            return "\n".join(argument_parts)

        elif differential <= -1.0:
            # PG advantage
            argument_parts = [
                "QCAT LEGAL ARGUMENT: NDIS Goals Alignment Supports Public Guardian Appointment\n",
                "=" * 80,
                f"\n\nAnalysis of NDIS plan goals shows Public Guardian appointment better aligns "
                f"with client outcomes (PG: {pg_score}/10, Family: {family_score}/10, "
                f"Differential: {differential:+.1f}).",
                "\n\nThis finding supports the proposed guardianship arrangement.",
                "\n" + "=" * 80,
            ]
            return "\n".join(argument_parts)

        else:
            # Neutral
            return (
                "QCAT CONSIDERATION: NDIS Goals Analysis\n" + "=" * 80 + "\n\n"
                f"Analysis of NDIS plan goals shows neutral alignment between family guardianship "
                f"({family_score}/10) and Public Guardian ({pg_score}/10), with minimal differential "
                f"({differential:+.1f}). Other factors should guide the guardianship decision.\n"
                + "=" * 80
            )

    @staticmethod
    def _generate_summary(
        goals_analysis: List[NDISGoal],
        family_score: float,
        pg_score: float,
        differential: float,
    ) -> str:
        """Generate executive summary"""

        summary_parts = [
            f"NDIS Goals Alignment Analysis - Executive Summary\n",
            f"\nOverall Alignment Scores:",
            f"- Family Guardianship: {family_score}/10",
            f"- Public Guardian: {pg_score}/10",
            f"- Differential: {differential:+.1f}\n",
        ]

        if differential >= 2.0:
            summary_parts.append(
                f"\nFINDING: Strong evidence that family guardianship better aligns with NDIS goals. "
                f"The {differential:.1f} point advantage demonstrates that family guardianship is more "
                f"likely to support the client in achieving their NDIS plan outcomes across multiple goal areas."
            )
        elif differential >= 0.5:
            summary_parts.append(
                f"\nFINDING: Evidence indicates family guardianship better aligns with NDIS goals. "
                f"The analysis shows family guardianship provides better support for the client's "
                f"goals and preferences as expressed in their NDIS plan."
            )
        elif differential <= -2.0:
            summary_parts.append(
                f"\nFINDING: Strong evidence that Public Guardian appointment better aligns with NDIS goals."
            )
        elif differential <= -0.5:
            summary_parts.append(
                f"\nFINDING: Evidence indicates Public Guardian appointment better aligns with NDIS goals."
            )
        else:
            summary_parts.append(
                f"\nFINDING: Neutral - both guardianship options show similar alignment with NDIS goals."
            )

        # Add goal-by-goal summary
        summary_parts.append("\n\nGoal-by-Goal Results:")
        for goal in goals_analysis:
            diff = goal.family_alignment_score - goal.pg_alignment_score
            winner = "Family" if diff > 0 else "PG" if diff < 0 else "Neutral"
            summary_parts.append(
                f"- {goal.goal_number} ({goal.goal_name}): {winner} (F:{goal.family_alignment_score}, PG:{goal.pg_alignment_score})"
            )

        summary_parts.append(
            f"\n\nQCAT Relevance: This analysis directly addresses Guardianship and Administration Act 2000 (Qld) "
            f"General Principle 5 (consideration of adult's will and preferences). The NDIS plan represents "
            f"the client's goals and preferences, making this alignment analysis critical to the guardianship decision."
        )

        return "\n".join(summary_parts)


# Main service function

async def analyze_goals_guardianship_alignment(
    request: GoalsAlignmentRequest,
) -> GoalsAlignmentResponse:
    """
    Tool 20: Analyze NDIS goals alignment with guardianship options.
    CRITICAL TOOL for QCAT appeals - demonstrates which guardianship option
    better supports client outcomes.
    """
    return await NDISGoalsAnalyzer.analyze_goals_alignment(request)
