"""
Automated Pipeline Test Suite
Tests text extraction, cleaning, skill taxonomy, TF-IDF scoring, and candidate ranking.
"""
import pytest
from pathlib import Path
from src.cleaner import clean_text, extract_contact_info
from src.skills import extract_skills, extract_years_experience, extract_education, analyze_skill_gaps
from src.matcher import compute_tfidf_similarity, calculate_candidate_score, rank_resumes
from src.extractor import load_all_resumes


def test_clean_text():
    sample = "Hello World! Visit https://example.com or email test@example.com. C++ & Python 3.10!"
    cleaned = clean_text(sample)
    assert "https" not in cleaned
    assert "test@example.com" not in cleaned
    assert "c++" in cleaned
    assert "python" in cleaned


def test_extract_contact_info():
    sample = "John Doe\nEmail: john.doe@work.com | Phone: +91 98765 43210\nLinkedIn: linkedin.com/in/johndoe"
    contact = extract_contact_info(sample)
    assert contact["email"] == "john.doe@work.com"
    assert "98765" in contact["phone"]
    assert "linkedin.com/in/johndoe" in contact["linkedin"]


def test_skill_extraction():
    text = "Proficient in Python, Sklearn, SQL, Docker, and Natural Language Processing."
    skills = extract_skills(text)
    assert "python" in skills
    assert "scikit-learn" in skills  # resolved from sklearn alias
    assert "sql" in skills
    assert "docker" in skills
    assert "nlp" in skills           # resolved from natural language processing


def test_experience_extraction():
    text_1 = "Senior Developer with 4.5 years of experience in distributed systems."
    text_2 = "Experience of 3 years building web apps."
    assert extract_years_experience(text_1) == 4.5
    assert extract_years_experience(text_2) == 3.0


def test_skill_gap_analysis():
    candidate_skills = ["python", "sql", "git"]
    required_skills = ["python", "sql", "docker", "fastapi"]
    gaps = analyze_skill_gaps(candidate_skills, required_skills)
    assert gaps["total_matched"] == 2
    assert "docker" in gaps["missing_skills"]
    assert "fastapi" in gaps["missing_skills"]


def test_calculate_candidate_score():
    score, breakdown = calculate_candidate_score(
        tfidf_sim=0.35,
        must_have_hits=5,
        must_have_total=5,
        years_exp=3.0,
        min_exp_required=2.0
    )
    assert 0.80 <= score <= 1.0
    assert breakdown["score_percentage"] >= 80.0


def test_end_to_end_ranking():
    parsed_resumes = load_all_resumes("resumes")
    assert len(parsed_resumes) >= 4
    
    jd = Path("data/job_description.txt").read_text(encoding="utf-8")
    df = rank_resumes(parsed_resumes, jd)
    
    assert not df.empty
    assert "rank" in df.columns
    assert "score" in df.columns
    assert "status" in df.columns
    # Top candidate should be shortlisted
    assert df.iloc[0]["status"] in ["Shortlisted", "Under Review"]
    # Unrelated candidate (Vikas Kumar) should have lowest score
    last_row = df.iloc[-1]
    assert last_row["score"] <= 0.20
