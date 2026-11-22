"""
Automated Resume Screening Tool - Main Orchestration Script
Runs the end-to-end NLP screening pipeline from terminal:
1. Ingests multi-format resumes (.pdf, .docx, .txt)
2. Reads Job Description
3. Computes TF-IDF vectorization and cosine similarity
4. Extracts skills, experience, and educational qualifications
5. Computes explainable candidate match scores & shortlist decisions
6. Exports rankings to CSV and summary reports to outputs/
7. Evaluates scoring metrics on benchmark data
"""
import sys
import json
import argparse
from pathlib import Path
import pandas as pd

from src.extractor import load_all_resumes
from src.matcher import rank_resumes
from src.skills import extract_skills, extract_jd_requirements
from src.evaluator import evaluate_ranking_performance, print_evaluation_report


def run_pipeline(
    resumes_dir: str = "resumes",
    jd_path: str = "data/job_description.txt",
    taxonomy_path: str = "data/skills_taxonomy.json",
    eval_csv_path: str = "data/labeled_pairs.csv",
    output_dir: str = "outputs",
    min_exp_years: float = 2.0
):
    print("\n" + "=" * 70)
    print("      AUTOMATED RESUME SCREENING & ATS CANDIDATE RANKING SYSTEM      ")
    print("=" * 70)
    
    # Ensure outputs directory exists
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load Job Description
    p_jd = Path(jd_path)
    if not p_jd.exists():
        print(f"[Error] Job description file not found at {jd_path}")
        sys.exit(1)
        
    jd_text = p_jd.read_text(encoding="utf-8", errors="ignore")
    print(f"[*] Loaded Job Description from: {jd_path}")
    
    # Extract Must-Have and Nice-to-Have Skills from JD
    jd_reqs = extract_jd_requirements(jd_text, taxonomy_path)
    must_have_skills = jd_reqs["must_have"]
    nice_to_have_skills = jd_reqs["nice_to_have"]
    
    print(f"[*] Target Must-Have Skills ({len(must_have_skills)}):")
    print(f"    -> {', '.join(must_have_skills)}")
    if nice_to_have_skills:
        print(f"[*] Nice-To-Have Skills ({len(nice_to_have_skills)}):")
        print(f"    -> {', '.join(nice_to_have_skills)}\n")
    else:
        print()
    
    # 2. Ingest Resumes
    print(f"[*] Scanning resumes in: '{resumes_dir}' ...")
    resumes = load_all_resumes(resumes_dir)
    if not resumes:
        print(f"[Warning] No valid resumes found in '{resumes_dir}'. Please add PDF, DOCX, or TXT files.")
        sys.exit(1)
        
    print(f"[+] Successfully ingested {len(resumes)} resumes.\n")
    
    # 3. Match, Score & Rank Candidates
    print("[*] Computing TF-IDF vectorization, Cosine Similarity, and Skill Gap Analysis...")
    df_ranked = rank_resumes(
        parsed_resumes=resumes,
        job_description=jd_text,
        must_have_skills=must_have_skills,
        min_exp_years=min_exp_years,
        taxonomy_path=taxonomy_path
    )
    
    # 4. Display Results Table in Terminal
    print("\n" + "-" * 70)
    print("                      CANDIDATE RANKING TABLE                        ")
    print("-" * 70)
    
    display_cols = ["rank", "candidate_name", "score_pct", "status", "years_exp", "matched_skills", "missing_skills"]
    # Pretty print columns
    header = f"{'Rank':<5} | {'Candidate Name':<16} | {'Score':<7} | {'Status':<14} | {'Exp(Y)':<6} | {'Matched Skills'}"
    print(header)
    print("-" * 70)
    for _, row in df_ranked.iterrows():
        matched_preview = (row['matched_skills'][:28] + '...') if len(row['matched_skills']) > 28 else row['matched_skills']
        print(f"{row['rank']:<5} | {row['candidate_name']:<16} | {row['score_pct']:<7} | {row['status']:<14} | {row['years_exp']:<6.1f} | {matched_preview}")
    print("-" * 70 + "\n")
    
    # 5. Export to CSV
    csv_out_path = out_dir / "ranked_candidates.csv"
    df_ranked.to_csv(csv_out_path, index=False)
    print(f"[+] Exported detailed ranking spreadsheet: {csv_out_path}")
    
    # 6. Generate Executive Shortlisting Summary Report
    summary_path = out_dir / "screening_summary.txt"
    shortlisted = df_ranked[df_ranked["status"] == "Shortlisted"]
    review = df_ranked[df_ranked["status"] == "Under Review"]
    rejected = df_ranked[df_ranked["status"] == "Rejected"]
    
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("AUTOMATED RESUME SCREENING - EXECUTIVE HIRING REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total Applicants Processed : {len(df_ranked)}\n")
        f.write(f"Shortlisted Candidates     : {len(shortlisted)}\n")
        f.write(f"Under Review Candidates    : {len(review)}\n")
        f.write(f"Rejected Candidates        : {len(rejected)}\n\n")
        
        f.write("-" * 60 + "\n")
        f.write("TOP RECOMMENDED CANDIDATES FOR INTERVIEW:\n")
        f.write("-" * 60 + "\n")
        for _, c in shortlisted.iterrows():
            f.write(f"• Rank #{c['rank']}: {c['candidate_name']} ({c['score_pct']})\n")
            f.write(f"  Contact  : {c['email']} | {c['phone']}\n")
            f.write(f"  Rationale: {c['reasons']}\n\n")
            
        f.write("-" * 60 + "\n")
        f.write("CANDIDATES REJECTED / DISQUALIFIED:\n")
        f.write("-" * 60 + "\n")
        for _, c in rejected.iterrows():
            f.write(f"• {c['candidate_name']} ({c['score_pct']}) - Missing: {c['missing_skills']}\n")
            
    print(f"[+] Exported executive recruiter summary: {summary_path}")
    
    # 7. Model Evaluation on Labeled Benchmark
    p_eval = Path(eval_csv_path)
    if p_eval.exists():
        try:
            metrics = evaluate_ranking_performance(p_eval)
            print_evaluation_report(metrics)
            metrics_out_path = out_dir / "evaluation_metrics.json"
            with open(metrics_out_path, "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=2)
            print(f"[+] Exported evaluation metrics JSON: {metrics_out_path}")
        except Exception as e:
            print(f"[Warning] Evaluation skipped: {e}")
            
    print("=" * 70)
    print(" [SUCCESS] SCREENING PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Resume Screening Tool CLI")
    parser.add_argument("--resumes", type=str, default="resumes", help="Path to resumes directory")
    parser.add_argument("--jd", type=str, default="data/job_description.txt", help="Path to Job Description file")
    parser.add_argument("--taxonomy", type=str, default="data/skills_taxonomy.json", help="Skills taxonomy JSON path")
    parser.add_argument("--eval", type=str, default="data/labeled_pairs.csv", help="Benchmark evaluation CSV")
    parser.add_argument("--output", type=str, default="outputs", help="Output directory for CSV and reports")
    parser.add_argument("--min_exp", type=float, default=2.0, help="Minimum required years of experience")
    
    args = parser.parse_args()
    run_pipeline(
        resumes_dir=args.resumes,
        jd_path=args.jd,
        taxonomy_path=args.taxonomy,
        eval_csv_path=args.eval,
        output_dir=args.output,
        min_exp_years=args.min_exp
    )
