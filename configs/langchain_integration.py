"""
Agnovat Analyst - LangChain Integration Example
Demonstrates how to use Agnovat tools in LangChain agents
"""

from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from typing import Dict, Any
import requests
import json

# Base configuration
AGNOVAT_BASE_URL = "http://localhost:8000/api"


class AgnovatTools:
    """Wrapper class for Agnovat Analyst tools"""

    @staticmethod
    def call_tool(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generic method to call any Agnovat tool"""
        response = requests.post(f"{AGNOVAT_BASE_URL}/{endpoint}", json=payload)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def analyze_bias(file_path: str) -> str:
        """Tool 5: Analyze document for bias and racism"""
        result = AgnovatTools.call_tool(
            "analysis/analyze-racism-bias", {"file_path": file_path}
        )
        return json.dumps(result, indent=2)

    @staticmethod
    def extract_family_support(file_path: str) -> str:
        """Tool 10: Extract family support evidence"""
        result = AgnovatTools.call_tool(
            "analysis/extract-family-support", {"file_path": file_path}
        )
        return json.dumps(result, indent=2)

    @staticmethod
    def analyze_ndis_goals(file_path: str, context: str = "Family guardianship") -> str:
        """Tool 20: NDIS Goals Alignment Analysis (CRITICAL)"""
        result = AgnovatTools.call_tool(
            "legal/goals-guardianship-alignment",
            {"file_path": file_path, "guardianship_context": context},
        )
        return json.dumps(result, indent=2)

    @staticmethod
    def generate_qcat_bundle(
        client_name: str, case_number: str, documents: list
    ) -> str:
        """Tool 23: Generate complete QCAT bundle"""
        result = AgnovatTools.call_tool(
            "reports/qcat-bundle",
            {
                "client_name": client_name,
                "case_number": case_number,
                "documents": documents,
            },
        )
        return json.dumps(result, indent=2)


# Create LangChain tools
tools = [
    Tool(
        name="analyze_bias",
        func=AgnovatTools.analyze_bias,
        description="""Analyze practitioner reports for bias, racism, and discrimination.
        Input should be an absolute file path to a PDF document.
        Returns detailed analysis with risk scores and flagged segments.""",
    ),
    Tool(
        name="extract_family_support",
        func=AgnovatTools.extract_family_support,
        description="""Extract evidence of family support and capacity from documents.
        Input should be an absolute file path to a PDF document.
        Returns 6 categories of family support evidence.""",
    ),
    Tool(
        name="analyze_ndis_goals",
        func=AgnovatTools.analyze_ndis_goals,
        description="""Analyze NDIS goals alignment with guardianship options.
        This is CRITICAL for demonstrating family guardianship advantage.
        Input should be an absolute file path to an NDIS plan PDF.
        Returns alignment scores for family vs Public Guardian.""",
    ),
    Tool(
        name="generate_qcat_bundle",
        func=lambda x: AgnovatTools.generate_qcat_bundle(
            "Client Name", "GAA123/2024", [x]
        ),
        description="""Generate complete QCAT evidence bundle.
        Input should be an absolute file path or comma-separated paths.
        Returns comprehensive bundle with all analyses and evidence.""",
    ),
]


# Example 1: Basic Agent Setup
def create_basic_agent():
    """Create a basic LangChain agent with Agnovat tools"""
    llm = ChatOpenAI(temperature=0, model="gpt-4")
    agent = initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )
    return agent


# Example 2: Specialized QCAT Agent
def create_qcat_agent():
    """Create specialized agent for QCAT analysis"""
    llm = ChatOpenAI(temperature=0, model="gpt-4")

    # Custom system message
    system_message = """You are a specialized assistant for QCAT guardianship appeals.
    You have access to 23 analysis tools through Agnovat Analyst.
    Always analyze documents for:
    1. Bias and discrimination
    2. Family capacity evidence
    3. NDIS goals alignment (CRITICAL)
    4. Legal framework compliance

    Provide clear, evidence-based recommendations."""

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={"system_message": system_message},
    )
    return agent


# Example usage
if __name__ == "__main__":
    # Create agent
    agent = create_qcat_agent()

    # Example query
    query = """
    I have a practitioner report at /path/to/report.pdf and an NDIS plan at
    /path/to/ndis_plan.pdf. Please analyze both for bias and NDIS goals alignment,
    then provide recommendations for my QCAT guardianship application.
    """

    # Run agent
    result = agent.run(query)
    print(result)


# Example 3: Chain of Thought Analysis
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


def analyze_document_chain(file_path: str):
    """Create a chain for comprehensive document analysis"""

    llm = ChatOpenAI(temperature=0)

    # Step 1: Analyze bias
    bias_result = AgnovatTools.analyze_bias(file_path)

    # Step 2: Extract family evidence
    family_result = AgnovatTools.extract_family_support(file_path)

    # Step 3: Synthesize findings
    synthesis_prompt = PromptTemplate(
        input_variables=["bias_analysis", "family_evidence"],
        template="""Based on the following analyses, provide a summary for QCAT submission:

Bias Analysis:
{bias_analysis}

Family Support Evidence:
{family_evidence}

Provide a concise summary highlighting:
1. Key bias concerns
2. Strongest family capacity evidence
3. Recommended next steps
""",
    )

    synthesis_chain = LLMChain(llm=llm, prompt=synthesis_prompt)

    summary = synthesis_chain.run(
        bias_analysis=bias_result, family_evidence=family_result
    )

    return summary


# Example 4: Multi-Document Analysis
def analyze_multiple_documents(document_paths: list):
    """Analyze multiple documents and synthesize results"""

    all_results = []

    for doc_path in document_paths:
        result = {
            "document": doc_path,
            "bias_analysis": AgnovatTools.analyze_bias(doc_path),
            "family_support": AgnovatTools.extract_family_support(doc_path),
        }
        all_results.append(result)

    return all_results


# Example 5: Complete QCAT Workflow
def complete_qcat_workflow(
    practitioner_reports: list, ndis_plan_path: str, client_name: str, case_number: str
):
    """Complete workflow from analysis to QCAT bundle generation"""

    print("Step 1: Analyzing practitioner reports for bias...")
    bias_analyses = [
        AgnovatTools.analyze_bias(report) for report in practitioner_reports
    ]

    print("Step 2: Extracting family support evidence...")
    family_evidence = [
        AgnovatTools.extract_family_support(report) for report in practitioner_reports
    ]

    print("Step 3: Analyzing NDIS goals alignment (CRITICAL)...")
    goals_analysis = AgnovatTools.analyze_ndis_goals(ndis_plan_path)

    print("Step 4: Generating complete QCAT bundle...")
    all_documents = practitioner_reports + [ndis_plan_path]
    bundle = AgnovatTools.generate_qcat_bundle(client_name, case_number, all_documents)

    return {
        "bias_analyses": bias_analyses,
        "family_evidence": family_evidence,
        "goals_analysis": goals_analysis,
        "qcat_bundle": bundle,
    }


# Testing
def test_agnovat_connection():
    """Test connection to Agnovat server"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Successfully connected to Agnovat Analyst")
            print(f"   Server status: {response.json()}")
            return True
        else:
            print("❌ Agnovat server returned error")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Agnovat server: {e}")
        print("   Make sure server is running: uvicorn app.main:app --reload")
        return False


if __name__ == "__main__":
    # Test connection first
    if test_agnovat_connection():
        print("\n✅ LangChain integration ready!")
        print("\nExample usage:")
        print("  agent = create_qcat_agent()")
        print('  result = agent.run("Analyze /path/to/report.pdf for bias")')
