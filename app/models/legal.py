"""
Legal Framework Analysis Models
Models for Tools 16-20: Human rights, guardianship risk, state bias, compliance, NDIS goals
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict

from app.models.base import RiskScore, AlignmentScore


# ============================================================================
# Tool 16: Human Rights Breaches
# ============================================================================

class HumanRightsBreach(BaseModel):
    """A single human rights breach"""
    right_category: str = Field(..., description="Category of right breached (e.g., Privacy, Cultural Rights)")
    legislation_section: str = Field(..., description="Relevant legislation section (e.g., 'Section 25')")
    breach_description: str = Field(..., description="Description of the breach")
    context: str = Field(..., description="Context surrounding the breach")
    severity: str = Field(..., description="Severity level: low, medium, high")
    page_number: Optional[int] = Field(None, description="Page number where breach occurs")
    legal_basis: str = Field(..., description="Legal basis for this breach category")


class HumanRightsBreachRequest(BaseModel):
    """Request to analyze human rights breaches"""
    file_path: str = Field(..., description="Path to PDF document")
    rights_focus: Optional[List[str]] = Field(
        default=None,
        description="Specific rights to focus on (privacy, culture, family, etc.)"
    )


class HumanRightsBreachResponse(BaseModel):
    """Response from human rights breach analysis"""
    breaches: List[HumanRightsBreach] = Field(..., description="List of identified breaches")
    total_breaches: int = Field(..., description="Total number of breaches found")
    risk_score: float = Field(..., description="Overall risk score (0-10)")
    analysis_summary: str = Field(..., description="Narrative summary of breaches")


# ============================================================================
# Tool 17: Guardianship Risk Assessment
# ============================================================================

class GuardianshipRiskAssessment(BaseModel):
    """Guardianship risk assessment results"""
    restrictiveness_score: float = Field(..., description="Least restrictive option score (0-10)")
    will_preferences_score: float = Field(..., description="Will and preferences consideration score (0-10)")
    family_involvement_score: float = Field(..., description="Family involvement score (0-10)")
    cultural_considerations_score: float = Field(..., description="Cultural considerations score (0-10)")
    evidence_quality_score: float = Field(..., description="Evidence quality score (0-10)")
    overall_compliance_score: float = Field(..., description="Overall compliance score (0-10)")
    risk_factors: List[str] = Field(..., description="Identified risk factors")
    protective_factors: List[str] = Field(..., description="Identified protective factors")
    compliance_issues: List[str] = Field(..., description="Compliance issues")
    recommendations: List[str] = Field(..., description="Recommendations")


class GuardianshipRiskRequest(BaseModel):
    """Request to analyze guardianship risk assessment"""
    file_path: str = Field(..., description="Path to PDF document")


class GuardianshipRiskResponse(BaseModel):
    """Response from guardianship risk assessment analysis"""
    assessment: GuardianshipRiskAssessment = Field(..., description="Risk assessment results")
    compliance_rating: str = Field(..., description="Overall compliance rating: high_compliance, moderate_compliance, low_compliance, non_compliant")
    analysis_summary: str = Field(..., description="Narrative summary")


# ============================================================================
# Tool 18: State Guardianship Bias Detection
# ============================================================================

class StateGuardianshipBiasRequest(BaseModel):
    """Request to detect bias toward state guardianship"""
    file_path: str = Field(..., description="Path to PDF document")


class StateGuardianshipBiasResponse(BaseModel):
    """Response from state guardianship bias detection"""
    bias_indicators: List[Dict] = Field(..., description="List of bias indicators with category, text, context")
    bias_score: float = Field(..., description="Bias score (0-10, higher = more bias)")
    bias_level: str = Field(..., description="Bias level: low, moderate, high")
    total_indicators: int = Field(..., description="Total number of bias indicators")
    analysis_summary: str = Field(..., description="Narrative summary")


# ============================================================================
# Tool 19: Professional Language Compliance
# ============================================================================

class ProfessionalComplianceRequest(BaseModel):
    """Request to analyze professional language compliance"""
    file_path: str = Field(..., description="Path to PDF document")


class ProfessionalComplianceResponse(BaseModel):
    """Response from professional language compliance analysis"""
    compliance_issues: List[Dict] = Field(..., description="List of compliance issues with category, issue, context, severity")
    compliance_score: float = Field(..., description="Compliance score (0-10, higher = better compliance)")
    compliance_level: str = Field(..., description="Compliance level: low, moderate, high")
    total_issues: int = Field(..., description="Total number of compliance issues")
    recommendations: List[str] = Field(..., description="Recommendations for improvement")
    analysis_summary: str = Field(..., description="Narrative summary")


# ============================================================================
# Tool 20: NDIS Goals Alignment (CRITICAL)
# ============================================================================

class NDISGoal(BaseModel):
    """NDIS Goal with alignment analysis"""
    goal_number: str = Field(..., description="Goal number (G1-G7)")
    goal_name: str = Field(..., description="Goal name")
    goal_description: str = Field(..., description="Full goal description")
    family_alignment_score: float = Field(..., description="Family guardianship alignment (0-10)")
    pg_alignment_score: float = Field(..., description="Public Guardian alignment (0-10)")
    evidence_for_family: List[str] = Field(..., description="Evidence supporting family alignment")
    evidence_against_pg: List[str] = Field(..., description="Evidence against PG alignment")
    analysis: str = Field(..., description="Detailed analysis")


class GoalsAlignmentRequest(BaseModel):
    """Request to analyze NDIS goals alignment"""
    file_path: str = Field(..., description="Path to PDF document with NDIS plan")
    guardianship_context: Optional[str] = Field(
        default=None,
        description="Context about guardianship decision"
    )


class GoalsAlignmentResponse(BaseModel):
    """Response from NDIS goals alignment analysis"""
    goals_analysis: List[NDISGoal] = Field(..., description="Analysis for each NDIS goal")
    overall_family_alignment: float = Field(..., description="Overall family alignment score (0-10)")
    overall_pg_alignment: float = Field(..., description="Overall PG alignment score (0-10)")
    alignment_differential: float = Field(..., description="Difference between family and PG alignment (positive favors family)")
    recommendation: str = Field(..., description="Guardianship recommendation based on goals")
    qcat_argument: str = Field(..., description="QCAT-ready argument based on goals analysis")
    analysis_summary: str = Field(..., description="Executive summary")
