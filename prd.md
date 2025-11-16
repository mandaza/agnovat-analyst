Document Integrity, Racism, Bias & Guardianship Alignment MCP
Product Requirements Document (PRD)
Version 1.1
Purpose: QCAT Guardianship Appeal Support
Confidential — Internal Legal & Family Advocacy Use Only
1. Overview
Internal MCP tool for analyzing practitioner reports to support appeals against transferring guardianship from parents to the Public Guardian.
2. Scope
• Internal-only system
• Evidence analysis for QCAT appeals
• Detects bias, fabrication, omissions, racism, and guardianship conflicts.
3. Core Objectives
• Identify misleading or biased practitioner statements.
• Extract evidence supporting family capacity.
• Compare recommendations.
• Analyze conflict with client’s NDIS goals.
4. Functional Requirements
• PDF extraction
• Racism/bias detection
• Fabrication & omission detection
• Guardianship risk analysis
• NDIS goal alignment scoring
5. MCP Tools
• extract_pdf_text
• analyze_pdf_for_racism
• compare_pdf_documents
• detect_inconsistent_statements
• detect_template_reuse
• extract_family_support_evidence
• analyze_goals_guardianship_alignment
6. Evidence Chain of Custody
• SHA-256 hashing
• Timestamping
• Integrity verification
7. Legal Framework
• Guardianship & Administration Act 2000 (Qld)
• Human Rights Act 2019 (Qld)
• Anti-Discrimination Act 1991 (Qld)
• NDIS Act 2013
• Racial Discrimination Act 1975 (Cth)
12. NDIS Goals & Guardianship Alignment Analysis
This section defines the analysis of how guardianship decisions (Family vs Public Guardian) support or conflict with the client's NDIS goals. The system evaluates practitioner reports, extracts evidence relevant to each goal, and produces alignment scores and legal narratives.
Purpose
To demonstrate to QCAT that the client's will, preferences, and NDIS goals are best supported through family guardianship, and that Public Guardian oversight may conflict with these goals.
NDIS Goals Covered
• G1 Business & Independence
• G2 Emotional Regulation & Communication
• G3 Family & Community Relationships
• G4 Cultural Responsibilities
• G5 Independent Living Skills
• G6 Sexual Relationships & Education
• G7 Community Participation & Social Networks
Input
• Client’s stated NDIS goals
• Full extracted text from practitioner's reports
• Guardian option under analysis
Output
• Per-goal alignment scores (0–10)
• Conflict detection flags
• Evidence supporting family involvement
• Evidence showing practitioner omission or misrepresentation
• Legal narrative report
Analysis Categories
• Goal support or hindrance
• Family involvement
• Public Guardian impact
• Omitted cultural/family elements
• Contradictions between reports and goals
QCAT Relevance
Supports arguments under:
• Human Rights Act 2019 s11–s16, s26–s29
• Guardianship principles: least restrictive option, will and preferences, support for decision-making.
