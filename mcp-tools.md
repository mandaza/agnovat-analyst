

# 🟦 **MCP TOOLS — FULL TEXT LIST**

---

# **1. extract_pdf_text**

**Purpose:** Extract full text, page-by-page text, and document statistics from a PDF.
**Input:** `file_path`
**Output:**

* `full_text`
* `pages[]`
* `stats{page_count, word_count, char_count}`
  **Used for:** All downstream analysis.

---

# **2. generate_document_hash**

**Purpose:** Create SHA-256 hash of the PDF for integrity and evidence chain-of-custody.
**Input:** `file_path`
**Output:**

* `hash`
* `timestamp`
  **Used for:** Ensuring evidence not altered.

---

# **3. verify_document_integrity**

**Purpose:** Confirm PDF has not been modified since submission.
**Input:** `file_path`, `expected_hash`
**Output:** `verified: true/false`
**Used for:** QCAT admissibility.

---

# **4. extract_metadata_and_timestamps**

**Purpose:** Extract metadata such as creation date, modification date, author.
**Input:** `file_path`
**Output:**

* `metadata{created, modified, author, software}`
  **Used for:** Detecting backdated or suspicious documents.

---

# **5. analyze_pdf_for_racism**

**Purpose:** Detect explicit racism, implicit bias, cultural insensitivity, and stigmatizing language.
**Input:** `file_path`, `client_name`
**Output:**

* `risk_scores`
* `flagged_segments`
* `narrative_report`
  **Used for:** Showing discriminatory reporting.

---

# **6. detect_inconsistent_statements**

**Purpose:** Identify contradictions across one or more practitioner documents.
**Input:** `documents[]`
**Output:**

* `contradictions[]`
* `severity_flag`
  **Examples:** inconsistent dates, different versions of events, changed severity levels.
  **Used for:** Discrediting practitioner reliability.

---

# **7. detect_template_reuse_and_copying**

**Purpose:** Detect copy/paste text used across multiple clients or multiple reports.
**Input:** `documents[]`
**Output:**

* `matching_blocks[]`
* `percentage_similarity`
  **Used for:** Proving assessments are generic or fabricated.

---

# **8. detect_omitted_context**

**Purpose:** Identify missing context such as antecedents, triggers, positive behaviours, family involvement.
**Input:** `full_text`
**Output:**

* `missing_context_items[]`
* `omission_severity_score`
  **Used for:** Demonstrating biased, one-sided reporting.

---

# **9. detect_non_evidence_based_statements**

**Purpose:** Flag statements with no evidence, dates, or examples (“the client is always aggressive”).
**Input:** `full_text`
**Output:**

* `unsupported_claims[]`
* `justification_score`
  **Used for:** Challenging validity of practitioner conclusions.

---

# **10. extract_family_support_evidence**

**Purpose:** Identify all mentions of family involvement, support, decision-making, emotional regulation, etc.
**Input:** `full_text`
**Output:**

* `family_support_instances[]`
* `themes{emotional, community, daily living, cultural, employment}`
  **Used for:** Showing parents are supportive and capable.

---

# **11. extract_public_guardian_limitations**

**Purpose:** Identify risks or negative impacts created by Public Guardian oversight.
**Input:** `full_text`
**Output:**

* `risk_items[]`
* `impact_on_goals`
  **Used for:** Showing Public Guardian may not align with client needs.

---

# **12. compare_pdf_documents**

**Purpose:** Compare two practitioner reports and highlight differences.
**Input:** `file_a`, `file_b`
**Output:**

* `similarity_score`
* `unique_content_a[]`
* `unique_content_b[]`
* `diff_summary`
  **Used for:** Showing changed recommendations or new claims.

---

# **13. analyze_and_compare_pdfs**

**Purpose:** Full analysis + comparison of two documents in a single tool.
**Input:** `file_a`, `file_b`
**Output:** Combined racism, bias, fabrication, and comparison report.
**Used for:** Identifying changes used to justify guardianship transfer.

---

# **14. extract_timeline_events**

**Purpose:** Extract all date+event pairs to build a timeline.
**Input:** `full_text`
**Output:** `timeline[]`
**Used for:** Showing patterns of involvement or misreporting.

---

# **15. generate_contradiction_matrix**

**Purpose:** Create structured contradictions table.
**Input:** `documents[]`
**Output:**

* rows: event/topic | version1 | version2 | conflict | explanation
  **Used for:** Highlighting unreliable practitioner evidence.

---

# **16. extract_human_rights_breaches**

**Purpose:** Map text to Qld Human Rights Act breaches.
**Input:** `full_text`
**Output:**

* `breaches{section, description, evidence}`
  **Used for:** Strong QCAT argument.

---

# **17. guardian_risk_assessment_analysis**

**Purpose:** Compare risk profile of FAMILY GUARDIANSHIP vs PUBLIC GUARDIAN.
**Input:** `family_evidence`, `pg_evidence`
**Output:**

* `family_risk_score`
* `pg_risk_score`
* `risk_comparison_report`
  **Used for:** Showing family option is least restrictive.

---

# **18. detect_bias_toward_state_guardianship**

**Purpose:** Detect language that pushes or prefers Public Guardian without evidence.
**Input:** `full_text`
**Output:**

* `bias_indicators[]`
* `severity_level`
  **Used for:** Demonstrating systemic or author bias.

---

# **19. analyze_professional_language_compliance**

**Purpose:** Assess whether practitioner uses appropriate, neutral, non-judgmental language.
**Input:** `full_text`
**Output:**

* `compliance_score`
* `problematic_language[]`
  **Used for:** Challenging quality of reports.

---

# **20. analyze_goals_guardianship_alignment**  ⭐ *New Critical Tool*

**Purpose:** Compare practitioner recommendations vs client’s NDIS goals.
**Input:**

* `goals[G1-G7]`
* `documents[]`
* `guardian_option (family/public)`
  **Output:**
* `alignment_scores`
* `goal_conflicts[]`
* `narrative_per_goal`
* `overall_alignment_summary`
  **Used for:** Showing guardianship change conflicts with the client’s goals, will, and preferences.

---

# **21. generate_guardianship_argument_report**

**Purpose:** Create a QCAT-ready legal narrative summarizing:

* Family capacity
* Practitioner inconsistencies
* Goal conflicts
* Bias indicators
* Human rights breaches
  **Input:** All previous tool outputs
  **Output:** `structured_legal_report`
  **Used for:** Submission to QCAT.

---

# **22. generate_qcat_evidence_summary**

**Purpose:** Generate a short but strong summary for QCAT.
**Input:** All tool outputs
**Output:**

* `summary_of_issues`
* `key_evidence_points`
* `breach_list`
* `guardian_recommendation`
  **Used for:** At the front of the QCAT evidence bundle.

---

# **23. generate_qcat_bundle**

**Purpose:** Assemble a complete QCAT evidence bundle.
**Input:** All documents + analysis
**Output:**

* `cover_page`
* `index`
* `summary_statement`
* `analysis_sections`
* `attachments_list`
  **Used for:** Filing to QCAT.

---

# 🟦 **END OF MCP TOOL LIST**


