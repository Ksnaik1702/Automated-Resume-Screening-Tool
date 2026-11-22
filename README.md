# 🎯 Automated Resume Screening Tool (AI & NLP-Powered ATS)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Recruiter_UI-red.svg)](https://streamlit.io/)
[![FastAPI Service](https://img.shields.io/badge/FastAPI-REST_API-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests: Pytest](https://img.shields.io/badge/Tests-Pytest_Passing-brightgreen.svg)](https://pytest.org/)

An industry-oriented Machine Learning & Natural Language Processing (NLP) Applicant Tracking System (ATS) that automatically ingests resumes (PDF, DOCX, TXT), cleans unstructured text, extracts skills & years of experience, performs TF-IDF cosine similarity against Job Descriptions, identifies critical must-have gaps, and produces explainable candidate rankings with executive reports.

---

## 📌 Project Overview & Problem Statement

### The Problem
In modern technical recruitment, a single job opening for software engineers or data analysts receives **250 to 1,000+ resumes**. Manually reading each resume is time-consuming (averaging 30–45 hours per requisition), error-prone, subjective, and introduces unconscious bias.

### The Solution
The **Automated Resume Screening Tool** acts as an intelligent initial recruiter copilot. It:
1. Automatically parses documents across heterogeneous formats (`.pdf`, `.docx`, `.txt`).
2. Extracts structured candidate entities (contact info, validated technical skills, years of experience, education).
3. Evaluates semantic relevance using **TF-IDF Vectorization** and **Cosine Similarity**.
4. Enforces hard rule constraints (Must-Have vs Nice-to-Have criteria, minimum experience gates).
5. Provides **explainable recruiter reasoning** for every candidate rather than an opaque black box score.
6. Exports auditable CSV ranking reports and provides both a **CLI pipeline**, an interactive **Streamlit Recruiter Dashboard**, and a **FastAPI REST backend**.

---

## 🏗️ System Architecture & Workflow

```
[ Candidate Resumes ]              [ Job Description ]
  (.pdf / .docx / .txt)                    (Text)
          │                                   │
          ▼                                   ▼
┌──────────────────┐               ┌──────────────────┐
│ Resume Ingestion │               │  JD Parser &     │
│ & Text Extraction│               │  Entity Mapper   │
└─────────┬────────┘               └─────────┬────────┘
          │                                   │
          ▼                                   ▼
┌─────────────────────────────────────────────────────┐
│          Text Normalization & Preprocessing         │
│  (Regex URL/Phone masking, Stopword noise removal)  │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│       Skills Taxonomy & Entity Extraction           │
│  (RapidFuzz token match, Years of Exp regex, Edu)   │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│             Hybrid ATS Scoring Engine               │
│  • TF-IDF Vectorization & Cosine Similarity (35%)   │
│  • Must-Have Skill Coverage Ratio (50%)             │
│  • Experience Requirement Gate (15%)                │
│  • Missing Must-Have Penalty (-2% per gap)          │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│          Auditable Recruiter Outputs                │
│  • Ranked Candidate Table (outputs/ranked_*.csv)    │
│  • Executive Hiring Summary (outputs/summary.txt)   │
│  • Interactive Streamlit Dashboard                  │
│  • FastAPI REST Endpoints                           │
└─────────────────────────────────────────────────────┘
```

---

## 🧰 Tech Stack

| Category | Tools / Libraries |
| :--- | :--- |
| **Language** | Python 3.10+ / 3.11 / 3.12 / 3.14 |
| **NLP & ML** | Scikit-learn (TF-IDF Vectorizer), RapidFuzz (fuzzy matching), NumPy, Pandas |
| **Document Parsers** | PyPDF2 (PDF extraction), python-docx (DOCX extraction), fpdf2 (synthetic data generation) |
| **Web UI** | Streamlit |
| **API Backend** | FastAPI, Uvicorn, Pydantic, SQLite |
| **Testing** | Pytest |

---

## 📁 Repository Structure

```
Automated-Resume-Screening-Tool/
├── data/
│   ├── job_description.txt        # Benchmark Job Description
│   ├── skills_taxonomy.json       # Canonical skill dictionary & aliases
│   └── labeled_pairs.csv          # Ground-truth evaluation benchmark
├── resumes/                       # Ingestion directory (PDF, DOCX, TXT)
│   ├── resume_aarav_sharma.pdf    # Senior Python Dev (Strong match)
│   ├── resume_priya_patel.docx    # Data Scientist (Strong match)
│   ├── resume_rohan_verma.pdf     # Backend Engineer (Moderate match)
│   ├── resume_neha_gupta.txt      # Junior Analyst (Entry level)
│   ├── resume_vikas_kumar.pdf     # Sales Executive (Disqualified profile)
│   └── resume_ananya_reddy.docx   # Frontend Developer (Role mismatch)
├── src/
│   ├── __init__.py                # Package initialization
│   ├── cleaner.py                 # Regex cleaning & contact extraction
│   ├── extractor.py               # Multi-format document parser
│   ├── skills.py                  # Skill taxonomy & experience parsing
│   ├── matcher.py                 # TF-IDF cosine similarity & hybrid scoring
│   └── evaluator.py               # Ranking evaluation metrics (ROC-AUC, PR-AUC)
├── outputs/
│   ├── ranked_candidates.csv      # Exported candidate rankings
│   ├── screening_summary.txt      # Executive recruiter brief
│   └── evaluation_metrics.json    # Model evaluation metrics
├── tests/
│   └── test_pipeline.py           # Pytest unit & regression tests
├── generate_sample_resumes.py     # Synthetic resume builder script
├── main.py                        # CLI pipeline entry point
├── app_streamlit.py               # Interactive recruiter dashboard
├── api/
│   └── app.py                     # FastAPI REST API endpoints
├── requirements.txt               # Project dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # Comprehensive documentation
```

---

## ⚡ Quick Start & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/Automated-Resume-Screening-Tool.git
cd Automated-Resume-Screening-Tool
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate Synthetic Sample Resumes (Optional)
```bash
python generate_sample_resumes.py
```

---

## 🚀 Running the Project

### Option 1: Command-Line Pipeline (CLI)
Run the complete end-to-end screening pipeline with one command:
```bash
python main.py
```
**Expected Terminal Output:**
```
======================================================================
      AUTOMATED RESUME SCREENING & ATS CANDIDATE RANKING SYSTEM      
======================================================================
[*] Loaded Job Description from: data/job_description.txt
[*] Target Must-Have Skills (11):
    -> data science, fastapi, flask, git, github, numpy, pandas, python, rest api, scikit-learn, sql

[*] Scanning resumes in: 'resumes' ...
[+] Successfully ingested 6 resumes.

[*] Computing TF-IDF vectorization, Cosine Similarity, and Skill Gap Analysis...

----------------------------------------------------------------------
                      CANDIDATE RANKING TABLE                        
----------------------------------------------------------------------
Rank  | Candidate Name   | Score   | Status         | Exp(Y) | Matched Skills
----------------------------------------------------------------------
1     | Aarav Sharma     | 82.3%   | Shortlisted    | 4.5    | fastapi, git, github, numpy,...
2     | Priya Patel      | 76.2%   | Shortlisted    | 3.2    | data science, flask, git, nu...
3     | Rohan Verma      | 37.7%   | Rejected       | 2.5    | fastapi, git, python, rest a...
4     | Neha Gupta       | 30.4%   | Rejected       | 1.5    | git, pandas, python, sql
5     | Ananya Reddy     | 15.7%   | Rejected       | 2.0    | git, github
6     | Vikas Kumar      | 3.0%    | Rejected       | 5.0    | 
----------------------------------------------------------------------

[+] Exported detailed ranking spreadsheet: outputs/ranked_candidates.csv
[+] Exported executive recruiter summary: outputs/screening_summary.txt
=======================================================
       MODEL EVALUATION & BENCHMARK METRICS       
=======================================================
  Area Under ROC Curve (ROC-AUC)   : 1.0000
  Precision-Recall AUC (PR-AUC)    : 1.0000
  Top-3 Candidate Precision        : 100.0%
  Top-5 Candidate Precision        : 80.0%
=======================================================
 [SUCCESS] SCREENING PIPELINE COMPLETED SUCCESSFULLY!
```

---

### Option 2: Interactive Streamlit Recruiter Dashboard
Launch the web interface for drag-and-drop resume upload and live gap exploration:
```bash
python -m streamlit run app_streamlit.py
```
Open your browser at `http://localhost:8501`.
Features:
- Live Job Description input
- Drag-and-drop resume uploader (multiple files)
- Real-time candidate ranking table with status filters
- Candidate inspection view with breakdown of matched skills vs missing gaps
- 1-click CSV download button

---

### Option 3: FastAPI REST Service
Run the backend API for third-party ATS integrations:
```bash
python -m uvicorn api.app:app --reload --port 8000
```
Access interactive Swagger UI documentation at `http://127.0.0.1:8000/docs`.
- `POST /job/create`: Create a job requirement.
- `POST /resume/upload`: Ingest a candidate resume file.
- `POST /rank/{job_id}`: Trigger scoring and fetch ranked JSON results.

---

### Option 4: Run Automated Tests
```bash
python -m pytest tests/test_pipeline.py -v
```
All 7 unit and integration tests will execute and validate data cleaning, skill extraction, regex experience parsing, and ranking.

---

## 📊 Sample Output: Candidate Report

| Rank | Candidate Name | Score | ATS Decision | Exp (Yrs) | Matched Must-Haves | Missing Gaps |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- |
| **1** | Aarav Sharma | **82.3%** | 🟢 **Shortlisted** | 4.5 | fastapi, git, github, numpy, pandas, python, rest api, scikit-learn, sql | data science, flask |
| **2** | Priya Patel | **76.2%** | 🟢 **Shortlisted** | 3.2 | data science, flask, git, numpy, pandas, python, scikit-learn, sql | fastapi, github, rest api |
| **3** | Rohan Verma | **37.7%** | 🔴 Rejected | 2.5 | fastapi, git, python, rest api, sql | data science, flask, numpy, pandas, scikit-learn |
| **4** | Neha Gupta | **30.4%** | 🔴 Rejected | 1.5 | git, pandas, python, sql | data science, fastapi, flask, scikit-learn |
| **5** | Ananya Reddy | **15.7%** | 🔴 Rejected | 2.0 | git, github | python, sql, pandas, scikit-learn, data science |
| **6** | Vikas Kumar | **3.0%** | 🔴 Rejected | 5.0 | None | all must-haves |

---

## ⚖️ Ethics, Bias & Compliance Controls
1. **PII Masking**: Emails, phone numbers, and physical addresses are segregated from TF-IDF vectorization and scoring inputs to prevent gender, ethnic, or regional proxy bias.
2. **Explainable Recommendations**: The tool outputs explicit rationales (e.g. *"Matched 9/11 must-haves; 4.5 yrs exp meets 2.0 yrs req"*) ensuring auditability and eliminating arbitrary black-box rejections.
3. **No Protected Attributes**: The feature extractor explicitly ignores demographics, age, gender, marital status, and religion.

---

## 🎓 Learning Outcomes
- Multi-format document parsing (`PyPDF2`, `python-docx`)
- Text preprocessing & feature extraction with Scikit-learn (`TfidfVectorizer`, Cosine Similarity)
- Taxonomy-guided entity and skill extraction with fuzzy string matching (`RapidFuzz`)
- RESTful microservice development with `FastAPI`
- Production-grade UI prototyping with `Streamlit`
- Automated test-driven development with `pytest`
