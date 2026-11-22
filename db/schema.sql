-- Automated Resume Screening Tool - Database Schema
-- SQLite / PostgreSQL compatible

CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  jd_text TEXT NOT NULL,
  must_have TEXT,           -- JSON array of required skills
  nice_to_have TEXT,        -- JSON array of preferred skills
  min_exp_years REAL DEFAULT 2.0,
  location TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidates (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  location TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resumes (
  candidate_id TEXT PRIMARY KEY REFERENCES candidates(id),
  source TEXT,              -- "pdf", "docx", "txt", "linkedin"
  raw_text TEXT,            -- full extracted text
  parsed_json TEXT,         -- structured fields: skills, years_exp, education
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS features (
  candidate_id TEXT REFERENCES candidates(id),
  job_id TEXT REFERENCES jobs(id),
  sim_embedding REAL,       -- cosine similarity (0.0 .. 1.0)
  rule_musthave_hits INT,   -- number of matched must-have skills
  rule_musthave_total INT,  -- total required must-have skills
  years_exp REAL,           -- extracted candidate experience in years
  gap_penalty REAL,         -- penalty score for missing skills
  PRIMARY KEY (candidate_id, job_id)
);

CREATE TABLE IF NOT EXISTS rankings (
  job_id TEXT REFERENCES jobs(id),
  candidate_id TEXT REFERENCES candidates(id),
  score REAL NOT NULL,      -- calibrated ATS composite score (0.0 .. 1.0)
  status TEXT NOT NULL,     -- "Shortlisted", "Under Review", "Rejected"
  reasons TEXT,             -- human-readable recruiter explanation
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (job_id, candidate_id)
);
