# ⚖️ Compliance, Bias Controls & Ethical AI Architecture

## 1. Ethical AI Principles in Hiring
Automated hiring systems are classified as **High-Risk AI Systems** under regulations such as the EU AI Act and New York City Local Law 144 (Automated Employment Decision Tools). Our architecture enforces strict privacy, bias mitigation, and auditability.

### A. PII Masking & Data Minimization
- Personal Identifiable Information (email, phone, physical location, names) is extracted and stored separately for recruiter contact purposes only.
- PII is **completely masked and omitted** from the NLP scoring matrix and TF-IDF feature space.
- Prevents geographical, gender, and socio-ethnic proxy bias.

### B. Prohibited Attributes Exclusion
The feature extractor strictly ignores and forbids:
- Gender
- Race and ethnicity
- Age and date of birth
- Religion
- Marital status
- Photo / appearance data

### C. Explainable Recruiter Audit Trails
- Black-box scoring is prohibited.
- For every candidate, the engine produces explicit audit trails:
  - Exact must-have skills matched vs missing
  - Stated years of experience vs required
  - Semantic content similarity
  - Transparent formula weight contributions

### D. Human-in-the-Loop Governance
The tool acts as a **recommender copilot**, never an autonomous decision-maker. All shortlisting and rejection decisions are reviewed and approved by human recruiters.
