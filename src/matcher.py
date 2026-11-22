"""
Resume-Job Description Matching and Scoring Module
Computes TF-IDF vectorization, Cosine Similarity, and an explainable hybrid ranking score.
"""
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from src.cleaner import clean_text
from src.skills import extract_skills, extract_years_experience, extract_education, analyze_skill_gaps


def compute_tfidf_similarity(job_description: str, resumes_text: List[str]) -> List[float]:
    """
    Computes cosine similarity between cleaned job description and each cleaned resume text
    using TF-IDF (Term Frequency-Inverse Document Frequency) vectorization.
    """
    if not resumes_text:
        return []
        
    cleaned_jd = clean_text(job_description)
    cleaned_resumes = [clean_text(r) for r in resumes_text]
    
    # Corpus: JD is document 0, resumes are documents 1..N
    corpus = [cleaned_jd] + cleaned_resumes
    
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),     # unigrams and bigrams for skill phrases (e.g. 'machine learning', 'power bi')
        max_df=0.95,
        min_df=1
    )
    
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # Vector for JD is tfidf_matrix[0]
    jd_vector = tfidf_matrix[0:1]
    resumes_vectors = tfidf_matrix[1:]
    
    # Since TfidfVectorizer produces L2 normalized vectors, dot product equals cosine similarity
    similarities = jd_vector.dot(resumes_vectors.T).toarray()[0]
    return [round(float(s), 4) for s in similarities]


def calculate_candidate_score(
    tfidf_sim: float,
    must_have_hits: int,
    must_have_total: int,
    years_exp: float,
    min_exp_required: float = 2.0,
    w_sim: float = 0.35,
    w_skills: float = 0.50,
    w_exp: float = 0.15,
    penalty_per_gap: float = 0.02
) -> Tuple[float, Dict[str, Any]]:
    """
    Computes a calibrated, explainable ATS score (0.0 to 1.0 or 0-100%).
    Formula:
    Score = (w_sim * Normalized_TFIDF) + (w_skills * Skill_Coverage) + (w_exp * Exp_Factor) - Gap_Penalty
    """
    skill_coverage = must_have_hits / max(1, must_have_total)
    
    # TF-IDF similarity normalized to [0, 1] relative to typical max (0.40)
    norm_sim = min(1.0, tfidf_sim / 0.35)
    
    # Experience factor (capped at 1.0)
    if min_exp_required > 0:
        exp_factor = min(1.0, years_exp / min_exp_required)
    else:
        exp_factor = 1.0
        
    missing_count = max(0, must_have_total - must_have_hits)
    gap_penalty = min(0.12, penalty_per_gap * missing_count)
    
    raw_score = (w_sim * norm_sim) + (w_skills * skill_coverage) + (w_exp * exp_factor) - gap_penalty
    final_score = max(0.0, min(1.0, raw_score))  # Clamp between 0.0 and 1.0
    
    breakdown = {
        "tfidf_sim": round(tfidf_sim, 4),
        "normalized_sim": round(norm_sim, 4),
        "skill_coverage": round(skill_coverage, 4),
        "exp_factor": round(exp_factor, 4),
        "gap_penalty": round(gap_penalty, 4),
        "raw_score": round(raw_score, 4),
        "final_score": round(final_score, 4),
        "score_percentage": round(final_score * 100, 1)
    }
    
    return round(final_score, 4), breakdown


def determine_status(score: float, missing_must_haves: int) -> str:
    """
    Determines shortlist decision: Shortlisted, Under Review, or Rejected.
    """
    if score >= 0.65 and missing_must_haves <= 3:
        return "Shortlisted"
    elif score >= 0.38:
        return "Under Review"
    else:
        return "Rejected"


def rank_resumes(
    parsed_resumes: List[Dict[str, Any]],
    job_description: str,
    must_have_skills: Optional[List[str]] = None,
    min_exp_years: float = 2.0,
    taxonomy_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Main orchestration function:
    1. Extracts skills, exp, and education from each resume
    2. Runs TF-IDF cosine similarity against JD
    3. Analyzes skill gaps
    4. Computes hybrid scoring and shortlist decisions
    5. Returns a sorted pandas DataFrame ranked by score descending
    """
    if not parsed_resumes:
        return pd.DataFrame()
        
    # Auto-extract must-have skills from JD if not explicitly provided
    if not must_have_skills:
        must_have_skills = extract_skills(job_description, taxonomy_path)
        # If still empty, default to primary keywords
        if not must_have_skills:
            must_have_skills = ["python", "sql", "git"]
            
    resumes_text = [r["raw_text"] for r in parsed_resumes]
    similarities = compute_tfidf_similarity(job_description, resumes_text)
    
    results = []
    
    for idx, r in enumerate(parsed_resumes):
        raw_text = r["raw_text"]
        cand_skills = extract_skills(raw_text, taxonomy_path)
        cand_exp = extract_years_experience(raw_text)
        cand_edu = extract_education(raw_text)
        
        gaps = analyze_skill_gaps(cand_skills, must_have_skills)
        tfidf_sim = similarities[idx]
        
        score, breakdown = calculate_candidate_score(
            tfidf_sim=tfidf_sim,
            must_have_hits=gaps["total_matched"],
            must_have_total=gaps["total_required"],
            years_exp=cand_exp,
            min_exp_required=min_exp_years
        )
        
        status = determine_status(score, len(gaps["missing_skills"]))
        
        # Explainable recruiter reason
        reason = (
            f"Matched {gaps['total_matched']}/{gaps['total_required']} must-haves; "
            f"TF-IDF sim: {tfidf_sim:.2f}; "
            f"{cand_exp:.1f} yrs exp (Req: {min_exp_years:.1f}); "
            f"Missing: {', '.join(gaps['missing_skills']) if gaps['missing_skills'] else 'None'}"
        )
        
        results.append({
            "rank": 0,  # will update after sort
            "candidate_name": r["candidate_name"],
            "filename": r["filename"],
            "score": score,
            "score_pct": f"{score * 100:.1f}%",
            "status": status,
            "matched_skills": ", ".join(gaps["matched_skills"]),
            "missing_skills": ", ".join(gaps["missing_skills"]),
            "years_exp": cand_exp,
            "education": ", ".join(cand_edu),
            "email": r["contact"]["email"],
            "phone": r["contact"]["phone"],
            "tfidf_similarity": tfidf_sim,
            "reasons": reason
        })
        
    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values(by="score", ascending=False).reset_index(drop=True)
        df["rank"] = df.index + 1
        
    return df
