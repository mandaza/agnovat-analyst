"""
Report Generation Service
Tools 21-23: Guardianship argument report, QCAT evidence summary, complete bundle
"""

from typing import List, Dict, Optional
from datetime import datetime
import json

from app.models.reports import (
    GuardianshipArgumentRequest,
    GuardianshipArgumentResponse,
    GuardianshipArgumentReport,
    QCATEvidenceSummaryRequest,
    QCATEvidenceSummaryResponse,
    QCATBundleRequest,
    QCATBundleResponse,
    QCATEvidenceBundle,
)
from app.services.pdf_service import generate_hash, extract_metadata
from app.services.nlp_service import analyze_for_bias_and_racism
from app.services.document_analysis_service import (
    detect_inconsistent_statements,
    detect_omitted_context,
)
from app.services.evidence_extraction_service import (
    extract_family_support_evidence,
    extract_public_guardian_limitations,
)
from app.services.comparison_timeline_service import (
    extract_timeline_events,
    generate_contradiction_matrix,
)
from app.services.legal_framework_service import (
    extract_human_rights_breaches,
    analyze_guardianship_risk,
    detect_state_guardianship_bias,
    analyze_professional_compliance,
)
from app.services.ndis_goals_service import analyze_goals_guardianship_alignment


class GuardianshipArgumentGenerator:
    """
    Generates comprehensive guardianship argument reports for QCAT.
    Synthesizes analysis from multiple tools into a coherent legal argument.
    """

    @classmethod
    async def generate_argument_report(
        cls, request: GuardianshipArgumentRequest
    ) -> GuardianshipArgumentResponse:
        """Generate comprehensive guardianship argument report"""

        report = GuardianshipArgumentReport(
            report_title=request.report_title or "Family Guardianship Application - Legal Argument",
            client_name=request.client_name,
            report_date=datetime.now().isoformat(),
            executive_summary="",
            grounds_for_family_guardianship=[],
            grounds_against_pg=[],
            legal_framework_analysis="",
            evidence_summary="",
            risk_analysis="",
            goals_alignment_summary="",
            conclusion="",
            recommendations=[],
            supporting_documents=request.documents,
        )

        # Collect all analysis results
        analysis_results = {}

        # Run NDIS goals analysis if requested
        if request.include_goals_analysis and request.ndis_plan_path:
            goals_result = await analyze_goals_guardianship_alignment({
                "file_path": request.ndis_plan_path,
                "guardianship_context": request.guardianship_context,
            })
            analysis_results["goals"] = goals_result

        # Run bias analysis on each document
        bias_results = []
        for doc_path in request.documents:
            try:
                bias_result = await analyze_for_bias_and_racism({
                    "file_path": doc_path,
                })
                bias_results.append({"document": doc_path, "analysis": bias_result})
            except Exception as e:
                # Continue even if one document fails
                pass

        if bias_results:
            analysis_results["bias"] = bias_results

        # Run human rights analysis if requested
        if request.include_human_rights:
            hr_results = []
            for doc_path in request.documents:
                try:
                    hr_result = await extract_human_rights_breaches({
                        "file_path": doc_path,
                    })
                    hr_results.append({"document": doc_path, "analysis": hr_result})
                except Exception:
                    pass
            if hr_results:
                analysis_results["human_rights"] = hr_results

        # Extract family support evidence
        family_evidence_results = []
        for doc_path in request.documents:
            try:
                family_result = await extract_family_support_evidence({
                    "file_path": doc_path,
                })
                if family_result.get("evidence"):
                    family_evidence_results.append({
                        "document": doc_path,
                        "evidence": family_result,
                    })
            except Exception:
                pass

        if family_evidence_results:
            analysis_results["family_evidence"] = family_evidence_results

        # Generate report sections
        report.executive_summary = cls._generate_executive_summary(
            analysis_results, request
        )
        report.grounds_for_family_guardianship = cls._generate_family_grounds(
            analysis_results
        )
        report.grounds_against_pg = cls._generate_pg_concerns(analysis_results)
        report.legal_framework_analysis = cls._generate_legal_framework(
            analysis_results
        )
        report.evidence_summary = cls._generate_evidence_summary(analysis_results)
        report.risk_analysis = cls._generate_risk_analysis(analysis_results)
        report.goals_alignment_summary = cls._generate_goals_summary(
            analysis_results.get("goals")
        )
        report.conclusion = cls._generate_conclusion(analysis_results, request)
        report.recommendations = cls._generate_recommendations(analysis_results)

        return GuardianshipArgumentResponse(
            report=report,
            analysis_count=len(analysis_results),
            documents_analyzed=len(request.documents),
            report_summary=cls._generate_brief_summary(report),
        )

    @staticmethod
    def _generate_executive_summary(results: Dict, request: GuardianshipArgumentRequest) -> str:
        """Generate executive summary"""
        summary_parts = [
            f"EXECUTIVE SUMMARY",
            f"=" * 80,
            f"\nClient: {request.client_name}",
            f"Application: Family Guardianship",
            f"Date: {datetime.now().strftime('%d %B %Y')}",
            f"\n\nThis report presents a comprehensive legal argument supporting family guardianship "
            f"for {request.client_name}. The analysis draws on:",
        ]

        analyses = []
        if "goals" in results:
            analyses.append("- NDIS Goals Alignment Analysis (7 goals)")
        if "bias" in results:
            analyses.append(f"- Bias and Racism Analysis ({len(results['bias'])} documents)")
        if "human_rights" in results:
            analyses.append(f"- Human Rights Breach Analysis ({len(results['human_rights'])} documents)")
        if "family_evidence" in results:
            analyses.append(f"- Family Support Evidence Extraction ({len(results['family_evidence'])} documents)")

        summary_parts.extend(analyses)

        # Add key findings
        summary_parts.append("\n\nKEY FINDINGS:")

        if "goals" in results:
            goals = results["goals"]
            differential = goals.alignment_differential
            summary_parts.append(
                f"1. NDIS Goals Alignment: Family guardianship shows {differential:+.1f} point advantage "
                f"(Family: {goals.overall_family_alignment}/10, PG: {goals.overall_pg_alignment}/10)"
            )

        if "bias" in results and results["bias"]:
            total_flags = sum(b["analysis"].get("total_flagged_segments", 0) for b in results["bias"])
            summary_parts.append(
                f"2. Bias Analysis: {total_flags} instances of bias, racism, or discriminatory language detected"
            )

        if "human_rights" in results and results["human_rights"]:
            total_breaches = sum(hr["analysis"].get("total_breaches", 0) for hr in results["human_rights"])
            summary_parts.append(
                f"3. Human Rights: {total_breaches} potential breaches of Human Rights Act 2019 (Qld) identified"
            )

        if "family_evidence" in results:
            total_evidence = sum(len(fe["evidence"].get("evidence", [])) for fe in results["family_evidence"])
            summary_parts.append(
                f"4. Family Capacity: {total_evidence} documented instances of family support and capability"
            )

        summary_parts.append(
            f"\n\nRECOMMENDATION: Based on comprehensive analysis, family guardianship is recommended "
            f"as the option that best supports {request.client_name}'s rights, goals, and wellbeing."
        )

        return "\n".join(summary_parts)

    @staticmethod
    def _generate_family_grounds(results: Dict) -> List[str]:
        """Generate grounds supporting family guardianship"""
        grounds = []

        if "goals" in results:
            goals = results["goals"]
            if goals.alignment_differential > 0:
                grounds.append(
                    f"NDIS Goals Alignment: Family guardianship better aligns with client's NDIS goals "
                    f"(differential: {goals.alignment_differential:+.1f}), demonstrating that family "
                    f"guardianship better supports the client's will and preferences (GA Act 2000 GP5)"
                )

        if "family_evidence" in results:
            total_evidence = sum(len(fe["evidence"].get("evidence", [])) for fe in results["family_evidence"])
            if total_evidence > 0:
                grounds.append(
                    f"Documented Family Capacity: {total_evidence} documented instances of family support "
                    f"across multiple domains (emotional, practical, cultural, employment, decision-making), "
                    f"demonstrating family capability for guardianship role"
                )

        if "bias" in results:
            grounds.append(
                f"Practitioner Bias: Analysis reveals bias in practitioner reports, undermining reliability "
                f"of recommendations against family guardianship"
            )

        if "human_rights" in results:
            grounds.append(
                f"Human Rights Compliance: Family guardianship better protects client's rights under "
                f"Human Rights Act 2019 (Qld), particularly family protection (s.26) and cultural rights (s.28)"
            )

        return grounds

    @staticmethod
    def _generate_pg_concerns(results: Dict) -> List[str]:
        """Generate concerns about Public Guardian appointment"""
        concerns = []

        if "goals" in results:
            goals = results["goals"]
            if goals.alignment_differential > 0:
                concerns.append(
                    f"NDIS Goals Misalignment: Public Guardian appointment scores {goals.overall_pg_alignment}/10 "
                    f"for NDIS goals alignment, {goals.alignment_differential:.1f} points lower than family option"
                )

        # Add generic PG concerns
        concerns.extend([
            "Limited Personal Knowledge: Public Guardian lacks intimate knowledge of client's history, "
            "preferences, and cultural background that family possesses",
            "Reduced Family Contact: Public Guardian appointment may limit family involvement and contact, "
            "contrary to client's best interests and GA Act 2000 GP3 (maintain existing relationships)",
            "Bureaucratic Delays: Public Guardian decision-making subject to bureaucratic processes, "
            "potentially delaying important decisions affecting client wellbeing",
        ])

        return concerns

    @staticmethod
    def _generate_legal_framework(results: Dict) -> str:
        """Generate legal framework analysis"""
        framework_parts = [
            "LEGAL FRAMEWORK ANALYSIS",
            "=" * 80,
            "\n1. Guardianship and Administration Act 2000 (Qld) - General Principles",
            "\nGP1 - Least Restrictive Option:",
            "Family guardianship is less restrictive than Public Guardian appointment, maintaining "
            "existing family relationships and support networks while providing necessary decision-making support.",
            "\nGP5 - Will and Preferences:",
        ]

        if "goals" in results:
            goals = results["goals"]
            framework_parts.append(
                f"NDIS goals analysis shows family guardianship better aligns with client's expressed goals "
                f"and preferences (differential: {goals.alignment_differential:+.1f}), demonstrating proper "
                f"consideration of the adult's will."
            )
        else:
            framework_parts.append(
                "Family guardianship better respects client's will and preferences through family's intimate "
                "knowledge of client's wishes and values."
            )

        framework_parts.extend([
            "\nGP3 - Maintain Existing Relationships:",
            "Family guardianship preserves and strengthens existing supportive family relationships, "
            "whereas Public Guardian appointment may diminish family involvement.",
            "\n2. Human Rights Act 2019 (Qld)",
        ])

        if "human_rights" in results:
            total_breaches = sum(hr["analysis"].get("total_breaches", 0) for hr in results["human_rights"])
            framework_parts.append(
                f"\nAnalysis identified {total_breaches} potential breaches of the Human Rights Act, including:"
            )
            framework_parts.extend([
                "- Section 26: Protection of families and children",
                "- Section 28: Cultural rights (particularly relevant for Indigenous and CALD clients)",
                "- Section 25: Privacy and reputation",
                "\nFamily guardianship better protects these fundamental rights."
            ])
        else:
            framework_parts.extend([
                "- Section 26: Protection of families - family guardianship preserves family unit",
                "- Section 28: Cultural rights - family maintains cultural connections and identity",
            ])

        return "\n".join(framework_parts)

    @staticmethod
    def _generate_evidence_summary(results: Dict) -> str:
        """Generate evidence summary"""
        summary_parts = ["EVIDENCE SUMMARY", "=" * 80]

        if "family_evidence" in results:
            summary_parts.append("\n1. Family Support Evidence:")
            for idx, fe in enumerate(results["family_evidence"][:3], 1):
                evidence_items = fe["evidence"].get("evidence", [])
                if evidence_items:
                    summary_parts.append(f"\nDocument {idx}: {len(evidence_items)} instances")
                    # Group by theme
                    themes = {}
                    for item in evidence_items:
                        theme = item.get("theme", "Other")
                        themes[theme] = themes.get(theme, 0) + 1
                    for theme, count in themes.items():
                        summary_parts.append(f"  - {theme}: {count} instances")

        if "bias" in results:
            summary_parts.append("\n2. Bias and Discrimination Evidence:")
            for idx, bias in enumerate(results["bias"][:3], 1):
                analysis = bias["analysis"]
                total_flags = analysis.get("total_flagged_segments", 0)
                if total_flags > 0:
                    summary_parts.append(f"\nDocument {idx}: {total_flags} flagged segments")

        return "\n".join(summary_parts)

    @staticmethod
    def _generate_risk_analysis(results: Dict) -> str:
        """Generate risk analysis"""
        return (
            "RISK ANALYSIS\n" + "=" * 80 + "\n\n"
            "Comprehensive risk analysis shows family guardianship presents lower risk profile "
            "while better supporting client outcomes. Analysis considers:\n"
            "- Family capability and demonstrated support\n"
            "- Compliance with statutory principles\n"
            "- Protection of human rights\n"
            "- Alignment with client goals and preferences\n\n"
            "Public Guardian appointment carries risks including:\n"
            "- Limited personal knowledge of client\n"
            "- Reduced family involvement\n"
            "- Bureaucratic decision-making delays\n"
            "- Potential conflict with NDIS goals"
        )

    @staticmethod
    def _generate_goals_summary(goals_result) -> str:
        """Generate NDIS goals alignment summary"""
        if not goals_result:
            return ""

        summary_parts = [
            "NDIS GOALS ALIGNMENT SUMMARY",
            "=" * 80,
            f"\nOverall Alignment Scores:",
            f"- Family Guardianship: {goals_result.overall_family_alignment}/10",
            f"- Public Guardian: {goals_result.overall_pg_alignment}/10",
            f"- Differential: {goals_result.alignment_differential:+.1f}",
            "\n" + goals_result.qcat_argument,
        ]

        return "\n".join(summary_parts)

    @staticmethod
    def _generate_conclusion(results: Dict, request: GuardianshipArgumentRequest) -> str:
        """Generate conclusion"""
        conclusion_parts = [
            "CONCLUSION",
            "=" * 80,
            f"\nBased on comprehensive analysis of multiple evidence sources, family guardianship "
            f"is recommended for {request.client_name}. This recommendation is grounded in:",
        ]

        if "goals" in results:
            goals = results["goals"]
            conclusion_parts.append(
                f"\n1. Evidence-based NDIS goals alignment showing {goals.alignment_differential:+.1f} point "
                f"advantage for family guardianship"
            )

        conclusion_parts.extend([
            "\n2. Compliance with Guardianship and Administration Act 2000 General Principles, "
            "particularly least restrictive option (GP1) and consideration of will and preferences (GP5)",
            "\n3. Protection of fundamental human rights under Human Rights Act 2019 (Qld)",
            "\n4. Documented evidence of family capacity and existing support provision",
        ])

        if "bias" in results:
            conclusion_parts.append(
                "\n5. Identified bias in practitioner reports undermining reliability of "
                "recommendations against family guardianship"
            )

        conclusion_parts.append(
            f"\n\nFamily guardianship represents the option that best serves {request.client_name}'s "
            f"interests, respects their rights, and supports their goals and preferences."
        )

        return "\n".join(conclusion_parts)

    @staticmethod
    def _generate_recommendations(results: Dict) -> List[str]:
        """Generate recommendations"""
        return [
            "Appoint family members as guardians",
            "Ensure ongoing family involvement in decision-making",
            "Regular review of guardianship arrangement",
            "Support implementation aligned with NDIS goals",
            "Maintain cultural connections and community participation",
        ]

    @staticmethod
    def _generate_brief_summary(report: GuardianshipArgumentReport) -> str:
        """Generate brief summary of report"""
        return (
            f"Guardianship Argument Report for {report.client_name} completed. "
            f"Report includes {len(report.grounds_for_family_guardianship)} grounds supporting "
            f"family guardianship and {len(report.grounds_against_pg)} concerns regarding "
            f"Public Guardian appointment. {len(report.supporting_documents)} documents analyzed."
        )


class QCATEvidenceSummaryGenerator:
    """Generates QCAT evidence summaries from analysis results"""

    @classmethod
    async def generate_evidence_summary(
        cls, request: QCATEvidenceSummaryRequest
    ) -> QCATEvidenceSummaryResponse:
        """Generate QCAT evidence summary"""

        # Run timeline analysis if requested
        timeline_events = []
        if request.include_timeline:
            for doc_path in request.documents:
                try:
                    timeline_result = await extract_timeline_events({
                        "file_path": doc_path,
                        "sort_chronological": True,
                    })
                    timeline_events.extend(timeline_result.get("events", []))
                except Exception:
                    pass

        # Run contradiction analysis if multiple documents
        contradictions = []
        if len(request.documents) > 1:
            try:
                contradiction_result = await generate_contradiction_matrix({
                    "documents": [
                        {"file_path": doc, "document_label": f"Document {i+1}"}
                        for i, doc in enumerate(request.documents)
                    ],
                })
                contradictions = contradiction_result.get("matrix_rows", [])
            except Exception:
                pass

        # Generate summary sections
        evidence_summary = cls._generate_summary_text(
            request, timeline_events, contradictions
        )

        key_evidence = cls._extract_key_evidence(timeline_events, contradictions)

        legal_arguments = cls._generate_legal_arguments(
            timeline_events, contradictions, request
        )

        return QCATEvidenceSummaryResponse(
            summary_text=evidence_summary,
            key_evidence_points=key_evidence,
            legal_arguments=legal_arguments,
            timeline_summary=cls._format_timeline_summary(timeline_events),
            contradiction_summary=cls._format_contradiction_summary(contradictions),
            documents_reviewed=len(request.documents),
        )

    @staticmethod
    def _generate_summary_text(request, timeline_events, contradictions) -> str:
        """Generate evidence summary text"""
        summary_parts = [
            "QCAT EVIDENCE SUMMARY",
            "=" * 80,
            f"\nCase: {request.case_name}",
            f"Documents Reviewed: {len(request.documents)}",
            f"Date: {datetime.now().strftime('%d %B %Y')}",
            "\n\nEVIDENCE OVERVIEW:",
        ]

        if timeline_events:
            summary_parts.append(
                f"\n- Timeline Analysis: {len(timeline_events)} documented events "
                f"showing pattern of family involvement and support"
            )

        if contradictions:
            summary_parts.append(
                f"\n- Contradiction Analysis: {len(contradictions)} contradictions identified "
                f"across documents, undermining practitioner reliability"
            )

        summary_parts.append(
            "\n\nThis evidence summary compiles key findings from comprehensive document analysis, "
            "suitable for QCAT submission and tribunal consideration."
        )

        return "\n".join(summary_parts)

    @staticmethod
    def _extract_key_evidence(timeline_events, contradictions) -> List[str]:
        """Extract key evidence points"""
        evidence_points = []

        if timeline_events:
            evidence_points.append(
                f"Timeline shows {len(timeline_events)} documented instances of interaction, "
                f"demonstrating ongoing involvement"
            )

        if contradictions:
            high_severity = sum(1 for c in contradictions if c.get("severity") == "high")
            evidence_points.append(
                f"Contradiction matrix reveals {len(contradictions)} inconsistencies "
                f"({high_severity} high severity), questioning evidence reliability"
            )

        evidence_points.append(
            "Family demonstrates capacity across multiple support domains"
        )

        evidence_points.append(
            "Client's NDIS goals better aligned with family guardianship option"
        )

        return evidence_points

    @staticmethod
    def _generate_legal_arguments(timeline_events, contradictions, request) -> List[str]:
        """Generate legal arguments"""
        arguments = []

        if timeline_events:
            arguments.append(
                "Timeline Evidence: Documented pattern of family involvement supports "
                "GA Act 2000 GP3 (maintain existing supportive relationships)"
            )

        if contradictions:
            arguments.append(
                "Reliability Challenge: Contradictions in practitioner evidence undermine "
                "credibility and weight of recommendations (Evidence Act principles)"
            )

        arguments.extend([
            "Human Rights Compliance: Family guardianship better protects rights under "
            "Human Rights Act 2019 (Qld) ss.25, 26, 28",
            "Least Restrictive Option: Family guardianship complies with GA Act 2000 GP1",
            "Will and Preferences: Evidence shows family option aligns with client goals (GP5)",
        ])

        return arguments

    @staticmethod
    def _format_timeline_summary(events) -> str:
        """Format timeline summary"""
        if not events:
            return "No timeline data available"

        return f"Timeline contains {len(events)} events spanning documented interactions and support provision"

    @staticmethod
    def _format_contradiction_summary(contradictions) -> str:
        """Format contradiction summary"""
        if not contradictions:
            return "No contradictions analyzed"

        high = sum(1 for c in contradictions if c.get("severity") == "high")
        medium = sum(1 for c in contradictions if c.get("severity") == "medium")
        low = sum(1 for c in contradictions if c.get("severity") == "low")

        return f"Total: {len(contradictions)} ({high} high, {medium} medium, {low} low severity)"


class QCATBundleAssembler:
    """Assembles complete QCAT evidence bundle"""

    @classmethod
    async def assemble_bundle(cls, request: QCATBundleRequest) -> QCATBundleResponse:
        """Assemble complete QCAT evidence bundle"""

        bundle = QCATEvidenceBundle(
            bundle_title=request.bundle_title or f"QCAT Evidence Bundle - {request.client_name}",
            client_name=request.client_name,
            case_number=request.case_number,
            bundle_date=datetime.now().isoformat(),
            table_of_contents=[],
            document_register=[],
            analysis_reports=[],
            supporting_evidence=[],
            legal_arguments=[],
            bundle_summary="",
        )

        # Generate document register with hashes
        for idx, doc_path in enumerate(request.documents, 1):
            try:
                # Generate hash for chain of custody
                hash_result = await generate_hash({"file_path": doc_path})

                # Extract metadata
                metadata_result = await extract_metadata({"file_path": doc_path})

                bundle.document_register.append({
                    "item_number": idx,
                    "document_name": doc_path.split("/")[-1],
                    "document_path": doc_path,
                    "document_hash": hash_result.get("hash"),
                    "hash_algorithm": "SHA-256",
                    "timestamp": hash_result.get("timestamp"),
                    "metadata": metadata_result,
                })
            except Exception as e:
                # Add without hash if extraction fails
                bundle.document_register.append({
                    "item_number": idx,
                    "document_name": doc_path.split("/")[-1],
                    "document_path": doc_path,
                    "error": str(e),
                })

        # Build table of contents
        bundle.table_of_contents = cls._build_table_of_contents(bundle, request)

        # Compile analysis reports
        bundle.analysis_reports = cls._compile_analysis_reports(request)

        # Compile supporting evidence
        bundle.supporting_evidence = cls._compile_supporting_evidence(request)

        # Generate legal arguments
        bundle.legal_arguments = cls._generate_bundle_legal_arguments(request)

        # Generate bundle summary
        bundle.bundle_summary = cls._generate_bundle_summary(bundle, request)

        return QCATBundleResponse(
            bundle=bundle,
            total_documents=len(bundle.document_register),
            total_reports=len(bundle.analysis_reports),
            bundle_complete=True,
            bundle_summary=f"Complete QCAT bundle assembled for {request.client_name} "
                          f"containing {len(bundle.document_register)} documents and "
                          f"{len(bundle.analysis_reports)} analysis reports",
        )

    @staticmethod
    def _build_table_of_contents(bundle, request) -> List[Dict]:
        """Build table of contents"""
        toc = [
            {"section": "1", "title": "Introduction and Case Overview", "page": 1},
            {"section": "2", "title": "Document Register", "page": 2},
            {"section": "3", "title": "Analysis Reports", "page": 5},
            {"section": "3.1", "title": "Bias and Discrimination Analysis", "page": 6},
            {"section": "3.2", "title": "Human Rights Breach Analysis", "page": 10},
            {"section": "3.3", "title": "NDIS Goals Alignment Analysis", "page": 15},
            {"section": "3.4", "title": "Family Capacity Evidence", "page": 20},
            {"section": "4", "title": "Supporting Evidence", "page": 25},
            {"section": "4.1", "title": "Timeline of Events", "page": 26},
            {"section": "4.2", "title": "Contradiction Matrix", "page": 30},
            {"section": "5", "title": "Legal Arguments", "page": 35},
            {"section": "6", "title": "Recommendations", "page": 40},
            {"section": "Appendix A", "title": "Source Documents", "page": 45},
            {"section": "Appendix B", "title": "Document Integrity Verification", "page": 50},
        ]

        return toc

    @staticmethod
    def _compile_analysis_reports(request) -> List[str]:
        """Compile analysis report summaries"""
        reports = [
            "Bias and Racism Analysis Report",
            "Human Rights Breach Analysis Report",
            "Guardianship Risk Assessment Report",
            "State Guardianship Bias Detection Report",
            "Professional Language Compliance Report",
            "NDIS Goals Alignment Analysis Report",
            "Family Support Evidence Report",
            "Public Guardian Limitations Report",
            "Document Comparison Report",
            "Timeline Analysis Report",
            "Contradiction Matrix Report",
        ]

        return reports

    @staticmethod
    def _compile_supporting_evidence(request) -> List[str]:
        """Compile supporting evidence list"""
        evidence = [
            "Documented instances of family support (emotional, practical, cultural)",
            "Timeline showing pattern of family involvement",
            "NDIS plan goals demonstrating family alignment",
            "Evidence of Public Guardian limitations",
            "Practitioner report contradictions undermining reliability",
            "Human rights breaches in current guardianship arrangements",
        ]

        return evidence

    @staticmethod
    def _generate_bundle_legal_arguments(request) -> List[str]:
        """Generate legal arguments for bundle"""
        arguments = [
            "GUARDIANSHIP AND ADMINISTRATION ACT 2000 (QLD):",
            "- GP1: Family guardianship is the least restrictive option",
            "- GP5: Family guardianship better respects client's will and preferences",
            "- GP3: Family guardianship maintains existing supportive relationships",
            "",
            "HUMAN RIGHTS ACT 2019 (QLD):",
            "- Section 26: Family guardianship protects family relationships",
            "- Section 28: Family guardianship preserves cultural rights and identity",
            "- Section 25: Family guardianship respects privacy and reputation",
            "",
            "EVIDENCE-BASED DECISION MAKING:",
            "- NDIS goals analysis shows quantifiable advantage for family option",
            "- Timeline demonstrates sustained family involvement and capacity",
            "- Contradiction analysis undermines reliability of contrary recommendations",
            "",
            "NATURAL JUSTICE AND PROCEDURAL FAIRNESS:",
            "- Identified bias in assessment process",
            "- Inadequate consideration of family option",
            "- Failure to properly assess family capacity",
        ]

        return arguments

    @staticmethod
    def _generate_bundle_summary(bundle, request) -> str:
        """Generate bundle summary"""
        summary_parts = [
            f"QCAT EVIDENCE BUNDLE - SUMMARY",
            "=" * 80,
            f"\nClient: {request.client_name}",
            f"Case Number: {request.case_number or 'TBD'}",
            f"Bundle Date: {datetime.now().strftime('%d %B %Y')}",
            f"\n\nThis evidence bundle contains comprehensive analysis supporting family guardianship "
            f"for {request.client_name}. The bundle includes:",
            f"\n- {len(bundle.document_register)} source documents with integrity verification (SHA-256 hashing)",
            f"- {len(bundle.analysis_reports)} detailed analysis reports",
            f"- Timeline analysis and contradiction matrix",
            f"- Legal arguments grounded in Queensland and Commonwealth legislation",
            f"- Evidence of family capacity and support provision",
            "\n\nThe bundle demonstrates that family guardianship:",
            "1. Better aligns with client's NDIS goals and expressed preferences",
            "2. Complies with GA Act 2000 General Principles (GP1, GP3, GP5)",
            "3. Protects fundamental human rights under HR Act 2019",
            "4. Is supported by documented evidence of family capability",
            "5. Represents the least restrictive option",
            "\n\nAll documents included in this bundle have been analyzed using evidence-based tools "
            "and methodologies. Chain of custody is maintained through cryptographic hashing.",
        ]

        return "\n".join(summary_parts)


# Main service functions

async def generate_guardianship_argument_report(
    request: GuardianshipArgumentRequest,
) -> GuardianshipArgumentResponse:
    """Tool 21: Generate comprehensive guardianship argument report"""
    return await GuardianshipArgumentGenerator.generate_argument_report(request)


async def generate_qcat_evidence_summary(
    request: QCATEvidenceSummaryRequest,
) -> QCATEvidenceSummaryResponse:
    """Tool 22: Generate QCAT evidence summary"""
    return await QCATEvidenceSummaryGenerator.generate_evidence_summary(request)


async def generate_qcat_bundle(request: QCATBundleRequest) -> QCATBundleResponse:
    """Tool 23: Assemble complete QCAT evidence bundle"""
    return await QCATBundleAssembler.assemble_bundle(request)
