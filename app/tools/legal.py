"""
Legal Framework Analysis Tools (Tools 16-20)
Human rights, guardianship risk, state bias, compliance, NDIS goals
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from app.models.legal import (
    HumanRightsBreachRequest,
    HumanRightsBreachResponse,
    GuardianshipRiskRequest,
    GuardianshipRiskResponse,
    StateGuardianshipBiasRequest,
    StateGuardianshipBiasResponse,
    ProfessionalComplianceRequest,
    ProfessionalComplianceResponse,
    GoalsAlignmentRequest,
    GoalsAlignmentResponse,
)
from app.services.legal_framework_service import (
    extract_human_rights_breaches as extract_hr_breaches_service,
    analyze_guardianship_risk as analyze_guardianship_service,
    detect_state_guardianship_bias as detect_bias_service,
    analyze_professional_compliance as analyze_compliance_service,
)
from app.services.ndis_goals_service import (
    analyze_goals_guardianship_alignment as analyze_goals_service,
)

router = APIRouter()


@router.post("/human-rights-breaches", response_model=HumanRightsBreachResponse)
async def extract_human_rights_breaches(request: HumanRightsBreachRequest):
    """
    Tool 16: Extract human rights breaches from practitioner reports.

    Analyzes documents for violations of:
    - Human Rights Act 2019 (Qld)
    - Guardianship and Administration Act 2000 (Qld)
    - UN Convention on Rights of Persons with Disabilities

    **Rights Categories:**
    - Privacy and Reputation (Section 25)
    - Protection of Families and Children (Section 26)
    - Cultural Rights (Section 28)
    - Freedom of Expression (Section 21)
    - Freedom of Movement (Section 19)
    - Right to Liberty (Section 29)

    **Use Case:** Supporting QCAT appeals by documenting rights violations
    """
    try:
        logger.info(f"Analyzing human rights breaches: {request.file_path}")
        result = await extract_hr_breaches_service(request)
        logger.info(f"Human rights analysis complete: {result.total_breaches} breaches found, risk score: {result.risk_score}/10")
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error analyzing human rights breaches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Human rights analysis failed: {str(e)}")


@router.post("/guardianship-risk-assessment", response_model=GuardianshipRiskResponse)
async def analyze_guardianship_risk_assessment(request: GuardianshipRiskRequest):
    """
    Tool 17: Analyze guardianship risk assessment quality and compliance.

    Evaluates compliance with Guardianship and Administration Act 2000 (Qld) principles:
    - Least restrictive option (General Principle 1)
    - Will and preferences (General Principle 5)
    - Family involvement consideration
    - Cultural appropriateness
    - Evidence quality

    **Scoring:**
    - 0-10 for each compliance dimension
    - Higher score = better compliance
    - Overall compliance rating provided

    **Use Case:** Challenging inadequate or non-compliant assessments
    """
    try:
        logger.info(f"Analyzing guardianship risk assessment: {request.file_path}")
        result = await analyze_guardianship_service(request)
        logger.info(f"Risk assessment analysis complete: {result.compliance_rating}, overall score: {result.assessment.overall_compliance_score}/10")
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error analyzing guardianship risk: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Guardianship risk analysis failed: {str(e)}")


@router.post("/detect-state-guardianship-bias", response_model=StateGuardianshipBiasResponse)
async def detect_bias_toward_state_guardianship(request: StateGuardianshipBiasRequest):
    """
    Tool 18: Detect bias toward state/public guardianship appointment.

    Identifies language patterns showing:
    - Preference for Public Guardian without justification
    - Dismissal of family capability
    - Idealization of state guardianship
    - Unsupported claims about family or state

    **Bias Categories:**
    - State Preference: Recommending PG without proper assessment
    - Family Dismissal: Negative generalizations about family
    - State Idealization: Unrealistic expectations of PG
    - Unsupported Claims: Generalizations without evidence

    **Use Case:** Demonstrating practitioner bias in QCAT appeals
    """
    try:
        logger.info(f"Detecting state guardianship bias: {request.file_path}")
        result = await detect_bias_service(request)
        logger.info(f"Bias detection complete: {result.bias_level} bias level, {result.total_indicators} indicators found")
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error detecting state guardianship bias: {str(e)}")
        raise HTTPException(status_code=500, detail=f"State guardianship bias detection failed: {str(e)}")


@router.post("/professional-language-compliance", response_model=ProfessionalComplianceResponse)
async def analyze_professional_language_compliance(request: ProfessionalComplianceRequest):
    """
    Tool 19: Analyze professional language compliance.

    Identifies non-person-centered, stigmatizing, or unprofessional language:
    - Deficit Language: Focus on deficits rather than strengths
    - Medical Model: "Suffering from" rather than social model
    - Labels Not People: "Disabled person" vs "person with disability"
    - Judgmental Language: "Difficult", "non-compliant", "refuses"
    - Unsupported Generalizations: "Always", "never", "typically"

    **Compliance Scoring:**
    - 10 = Perfect compliance (person-centered, professional)
    - 0 = Many compliance issues
    - Severity ratings: high, medium

    **Use Case:** Challenging practitioner credibility and professional standards
    """
    try:
        logger.info(f"Analyzing professional language compliance: {request.file_path}")
        result = await analyze_compliance_service(request)
        logger.info(f"Compliance analysis complete: {result.compliance_level} compliance, {result.total_issues} issues found")
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error analyzing professional compliance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Professional compliance analysis failed: {str(e)}")


@router.post("/goals-guardianship-alignment", response_model=GoalsAlignmentResponse)
async def analyze_goals_guardianship_alignment(request: GoalsAlignmentRequest):
    """
    Tool 20: Analyze NDIS goals alignment with guardianship options. ⭐ CRITICAL

    Evaluates which guardianship option (family vs Public Guardian) better aligns
    with the client's NDIS plan goals (G1-G7).

    **NDIS Goals Analyzed:**
    - G1: More choice and control
    - G2: Community participation
    - G3: Employment support
    - G4: Daily living skills
    - G5: Health and wellbeing
    - G6: Lifelong learning
    - G7: Social, community, and civic participation

    **Analysis:**
    - Family alignment score (0-10) per goal
    - Public Guardian alignment score (0-10) per goal
    - Differential calculation
    - Evidence-based recommendation
    - QCAT-ready argument

    **Use Case:** CRITICAL for QCAT appeals - demonstrating family guardianship
    better supports NDIS goals and client outcomes
    """
    try:
        logger.info(f"Analyzing NDIS goals alignment: {request.file_path}")
        result = await analyze_goals_service(request)
        logger.info(
            f"Goals alignment complete: Family {result.overall_family_alignment}/10, "
            f"PG {result.overall_pg_alignment}/10, Differential: {result.alignment_differential:+.1f}"
        )
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error analyzing goals alignment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Goals alignment analysis failed: {str(e)}")
