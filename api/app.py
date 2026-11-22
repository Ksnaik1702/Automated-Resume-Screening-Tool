"""
FastAPI Service for Automated Resume Screening
Exposes REST endpoints for Job Creation, Resume Ingestion, Scoring, and Ranking.
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import sqlite3
import uuid
import json
import io

from src.cleaner import clean_text
from src.extractor import extract_text_from_pdf, extract_text_from_docx, extract_contact_info, extract_candidate_name
from src.skills import extract_skills, extract_years_experience, extract_education
from src.matcher import rank_resumes

app = FastAPI(
    title="Automated Resume Screening ATS API",
    description="Production-grade RESTful API for candidate ingestion, skill extraction, and ATS ranking.",
    version="1.0.0"
)

DB_PATH = Path("data/screening.db")


def init_db():
    """Initializes normalized SQLite tables for jobs, resumes, and rankings."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        title TEXT,
        jd_text TEXT,
        must_have TEXT,
        min_exp_years REAL,
        location TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        candidate_id TEXT PRIMARY KEY,
        candidate_name TEXT,
        filename TEXT,
        raw_text TEXT,
        skills TEXT,
        years_exp REAL,
        email TEXT,
        phone TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS rankings (
        job_id TEXT,
        candidate_id TEXT,
        score REAL,
        status TEXT,
        reasons TEXT,
        PRIMARY KEY (job_id, candidate_id)
    );
    """)
    con.commit()
    con.close()


init_db()


class JobCreate(BaseModel):
    title: str
    jd_text: str
    must_have: Optional[List[str]] = []
    min_exp_years: float = 2.0
    location: Optional[str] = "Remote"


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Automated Resume Screening ATS"}


@app.post("/job/create")
def create_job(j: JobCreate):
    """Creates a new job description requirement."""
    job_id = str(uuid.uuid4())[:8]
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO jobs (id, title, jd_text, must_have, min_exp_years, location) VALUES (?, ?, ?, ?, ?, ?)",
        (job_id, j.title, j.jd_text, json.dumps(j.must_have), j.min_exp_years, j.location)
    )
    con.commit()
    con.close()
    return {"job_id": job_id, "title": j.title, "status": "Job created successfully"}


@app.post("/resume/upload")
async def upload_resume(
    candidate_id: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    """
    Ingests and parses a candidate resume (PDF, DOCX, or TXT).
    Extracts text, metadata, contacts, skills, and experience.
    """
    cid = candidate_id or str(uuid.uuid4())[:8]
    content = await file.read()
    suffix = Path(file.filename).suffix.lower()
    
    if suffix == ".pdf":
        raw_text = extract_text_from_pdf(io.BytesIO(content))
    elif suffix in [".docx", ".doc"]:
        raw_text = extract_text_from_docx(io.BytesIO(content))
    else:
        raw_text = content.decode("utf-8", errors="ignore")
        
    name = extract_candidate_name(raw_text, file.filename)
    contact = extract_contact_info(raw_text)
    skills = extract_skills(raw_text)
    years_exp = extract_years_experience(raw_text)
    
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO resumes 
    (candidate_id, candidate_name, filename, raw_text, skills, years_exp, email, phone)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (cid, name, file.filename, raw_text, json.dumps(skills), years_exp, contact["email"], contact["phone"]))
    con.commit()
    con.close()
    
    return {
        "candidate_id": cid,
        "candidate_name": name,
        "filename": file.filename,
        "extracted_skills": skills,
        "years_experience": years_exp,
        "email": contact["email"],
        "phone": contact["phone"]
    }


@app.post("/rank/{job_id}")
def rank_candidates_for_job(job_id: str):
    """
    Ranks all stored candidate resumes against a specific job requirement.
    """
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    
    job_row = cur.execute("SELECT id, title, jd_text, must_have, min_exp_years FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not job_row:
        con.close()
        raise HTTPException(status_code=404, detail=f"Job ID '{job_id}' not found.")
        
    jid, title, jd_text, must_have_json, min_exp = job_row
    must_haves = json.loads(must_have_json) if must_have_json else []
    
    cand_rows = cur.execute("SELECT candidate_id, candidate_name, filename, raw_text, email, phone FROM resumes").fetchall()
    if not cand_rows:
        con.close()
        return {"job_id": job_id, "message": "No candidates found in database to rank.", "rankings": []}
        
    parsed_resumes = []
    for r in cand_rows:
        parsed_resumes.append({
            "candidate_id": r[0],
            "candidate_name": r[1],
            "filename": r[2],
            "raw_text": r[3],
            "contact": {"email": r[4], "phone": r[5]}
        })
        
    df_ranked = rank_resumes(
        parsed_resumes=parsed_resumes,
        job_description=jd_text,
        must_have_skills=must_haves or None,
        min_exp_years=min_exp
    )
    
    # Store rankings
    for _, row in df_ranked.iterrows():
        cur.execute(
            "INSERT OR REPLACE INTO rankings (job_id, candidate_id, score, status, reasons) VALUES (?, ?, ?, ?, ?)",
            (job_id, row["candidate_name"], row["score"], row["status"], row["reasons"])
        )
    con.commit()
    con.close()
    
    return {
        "job_id": job_id,
        "job_title": title,
        "total_ranked": len(df_ranked),
        "rankings": df_ranked.to_dict(orient="records")
    }
