"""
Interactive Recruiter Dashboard - Automated Resume Screening Tool
Built with Streamlit for live candidate screening, skill gap inspection, and CSV export.
"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path
import io

from src.cleaner import clean_text
from src.extractor import extract_text_from_file, extract_contact_info, extract_candidate_name
from src.skills import extract_skills, extract_years_experience, extract_education, analyze_skill_gaps, extract_jd_requirements
from src.matcher import rank_resumes

st.set_page_config(
    page_title="Automated Resume Screening Tool",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F3F4F6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #3B82F6;
    }
    .shortlisted-badge {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .review-badge {
        background-color: #FEF08A;
        color: #854D0E;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .rejected-badge {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎯 Automated Resume Screening & ATS Ranking Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Industry-grade NLP candidate scoring, skill gap detection, and recruitment analytics.</div>', unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.header("⚙️ Screening Configuration")
taxonomy_file = "data/skills_taxonomy.json"
min_exp_input = st.sidebar.slider("Minimum Experience Required (Years)", min_value=0.0, max_value=10.0, value=2.0, step=0.5)

# Load Default Job Description if available
default_jd = ""
default_jd_path = Path("data/job_description.txt")
if default_jd_path.exists():
    default_jd = default_jd_path.read_text(encoding="utf-8", errors="ignore")

# Main Layout: 2 Columns
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("1. Job Description & Criteria")
    jd_input = st.text_area("Paste Job Description (JD):", value=default_jd, height=220)
    
    if jd_input.strip():
        reqs = extract_jd_requirements(jd_input, taxonomy_file)
        st.markdown(f"**Identified Must-Have Skills ({len(reqs['must_have'])}):**")
        st.write(", ".join(reqs["must_have"]))
        if reqs["nice_to_have"]:
            st.markdown(f"**Nice-to-Have Skills ({len(reqs['nice_to_have'])}):**")
            st.write(", ".join(reqs["nice_to_have"]))

with col_right:
    st.subheader("2. Upload Candidate Resumes")
    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, or TXT Resumes (Multi-file supported)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )
    
    use_samples = st.checkbox("Include 6 Pre-built Sample Resumes from 'resumes/' folder", value=True)

# Run Screening Button
st.markdown("---")
btn_run = st.button("🚀 Run Screening & Rank Candidates", type="primary", use_container_width=True)

if btn_run or "last_results" in st.session_state:
    if btn_run:
        if not jd_input.strip():
            st.error("Please provide a Job Description.")
            st.stop()
            
        parsed_resumes = []
        
        # 1. Process uploaded files
        if uploaded_files:
            for uf in uploaded_files:
                suffix = Path(uf.name).suffix.lower()
                bytes_data = uf.read()
                raw_text = ""
                if suffix == ".pdf":
                    from src.extractor import extract_text_from_pdf
                    raw_text = extract_text_from_pdf(io.BytesIO(bytes_data))
                elif suffix == ".docx":
                    from src.extractor import extract_text_from_docx
                    raw_text = extract_text_from_docx(io.BytesIO(bytes_data))
                else:
                    raw_text = bytes_data.decode("utf-8", errors="ignore")
                    
                contact = extract_contact_info(raw_text)
                name = extract_candidate_name(raw_text, uf.name)
                parsed_resumes.append({
                    "filename": uf.name,
                    "candidate_name": name,
                    "raw_text": raw_text,
                    "contact": contact
                })
                
        # 2. Process sample files if checked
        if use_samples:
            from src.extractor import load_all_resumes
            sample_resumes = load_all_resumes("resumes")
            # Avoid duplicate filenames
            existing_names = {r["filename"] for r in parsed_resumes}
            for s in sample_resumes:
                if s["filename"] not in existing_names:
                    parsed_resumes.append(s)
                    
        if not parsed_resumes:
            st.warning("No resumes found to evaluate. Please upload resumes or enable sample resumes.")
            st.stop()
            
        reqs = extract_jd_requirements(jd_input, taxonomy_file)
        must_haves = reqs["must_have"] or ["python", "sql", "git"]
        
        df_ranked = rank_resumes(
            parsed_resumes=parsed_resumes,
            job_description=jd_input,
            must_have_skills=must_haves,
            min_exp_years=min_exp_input,
            taxonomy_path=taxonomy_file
        )
        st.session_state["last_results"] = df_ranked
    else:
        df_ranked = st.session_state["last_results"]

    # Display KPI Metrics
    total = len(df_ranked)
    shortlisted = len(df_ranked[df_ranked["status"] == "Shortlisted"])
    review = len(df_ranked[df_ranked["status"] == "Under Review"])
    rejected = len(df_ranked[df_ranked["status"] == "Rejected"])
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Applicants", total)
    kpi2.metric("Shortlisted (>=65%)", shortlisted)
    kpi3.metric("Under Review", review)
    kpi4.metric("Rejected / Disqualified", rejected)
    
    st.markdown("### 📊 Ranked Candidate Leaderboard")
    
    filter_status = st.radio("Filter Status:", ["All", "Shortlisted", "Under Review", "Rejected"], horizontal=True)
    if filter_status != "All":
        filtered_df = df_ranked[df_ranked["status"] == filter_status]
    else:
        filtered_df = df_ranked
        
    # Table Display
    display_df = filtered_df[[
        "rank", "candidate_name", "filename", "score_pct", "status",
        "years_exp", "matched_skills", "missing_skills"
    ]].rename(columns={
        "rank": "Rank",
        "candidate_name": "Candidate",
        "filename": "Source File",
        "score_pct": "Match Score",
        "status": "Decision",
        "years_exp": "Exp (Yrs)",
        "matched_skills": "Matched Must-Haves",
        "missing_skills": "Missing Gaps"
    })
    
    st.dataframe(display_df, use_container_width=True)
    
    # Candidate Deep Dive Explorer
    st.markdown("### 🔍 Candidate Detailed Audit & Explanation")
    selected_name = st.selectbox("Select Candidate to inspect:", df_ranked["candidate_name"].tolist())
    
    if selected_name:
        cand_row = df_ranked[df_ranked["candidate_name"] == selected_name].iloc[0]
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"**Candidate:** `{cand_row['candidate_name']}`")
            st.markdown(f"**Contact:** 📧 `{cand_row['email']}` | 📱 `{cand_row['phone']}`")
            st.markdown(f"**Education:** {cand_row['education']}")
            st.markdown(f"**Experience:** {cand_row['years_exp']} Years")
            st.markdown(f"**TF-IDF Cosine Similarity:** `{cand_row['tfidf_similarity']}`")
        with c2:
            st.markdown(f"**Overall Score:** `{cand_row['score_pct']}`")
            st.markdown(f"**ATS Status:** **{cand_row['status']}**")
            st.markdown(f"**Skills Matched:** :green[{cand_row['matched_skills'] or 'None'}]")
            st.markdown(f"**Missing Gaps:** :red[{cand_row['missing_skills'] or 'None'}]")
            st.info(f"**Recruiter Rationale:** {cand_row['reasons']}")
            
    # Export Download Button
    csv_bytes = df_ranked.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Complete Screening Report (CSV)",
        data=csv_bytes,
        file_name="ats_candidate_screening_report.csv",
        mime="text/csv",
        use_container_width=True
    )
