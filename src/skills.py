"""
Skill Extraction and Experience Parsing Module
Provides taxonomy-guided skill identification, fuzzy matching, and experience detection.
"""
import re
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from rapidfuzz import process, fuzz


DEFAULT_SKILLS = [
    "python", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "sql", "postgresql", "mysql", "sqlite", "mongodb", "fastapi", "flask",
    "django", "docker", "kubernetes", "aws", "azure", "gcp", "git",
    "github", "linux", "nlp", "machine learning", "deep learning",
    "power bi", "tableau", "excel", "rest api", "data analysis",
    "c++", "java", "react", "node.js", "c"
]

DEFAULT_ALIASES = {
    "sklearn": "scikit-learn",
    "py": "python",
    "postgres": "postgresql",
    "ms excel": "excel",
    "natural language processing": "nlp",
    "ml": "machine learning",
    "dl": "deep learning",
    "bi": "power bi",
    "restful": "rest api",
    "rest apis": "rest api",
    "amazon web services": "aws",
    "google cloud": "gcp",
    "microsoft azure": "azure"
}


def load_taxonomy(json_path: Optional[str | Path] = None) -> Tuple[List[str], Dict[str, str]]:
    """Loads standardized skill list and alias dictionary from JSON file."""
    if json_path and Path(json_path).exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("skills", DEFAULT_SKILLS), data.get("aliases", DEFAULT_ALIASES)
        except Exception:
            pass
    return DEFAULT_SKILLS, DEFAULT_ALIASES


def extract_skills(text: str, taxonomy_path: Optional[str | Path] = None, fuzzy_cutoff: int = 88) -> List[str]:
    """
    Extracts validated skills from raw or cleaned text using high-speed exact taxonomy
    lookups, alias resolution, and targeted fuzzy matching.
    """
    skills_list, aliases = load_taxonomy(taxonomy_path)
    text_lower = text.lower()
    detected_skills: Set[str] = set()

    # 1. Exact phrase matching for multi-word and single-word skills (O(N_skills) regex lookups)
    for skill in skills_list:
        pattern = r'(?:\b|_)' + re.escape(skill) + r'(?:\b|_)'
        if re.search(pattern, text_lower):
            detected_skills.add(skill)

    # 2. Check aliases (e.g. sklearn -> scikit-learn, py -> python)
    for alias, canonical in aliases.items():
        pattern = r'(?:\b|_)' + re.escape(alias) + r'(?:\b|_)'
        if re.search(pattern, text_lower):
            detected_skills.add(canonical)

    # 3. Targeted fuzzy matching: only for remaining unmatched skills against candidate words
    unmatched_skills = [s for s in skills_list if s not in detected_skills and " " not in s and len(s) >= 4]
    if unmatched_skills:
        # Extract word tokens with length >= 4
        words = set(re.findall(r"\b[a-zA-Z\+\#\.\-]{4,15}\b", text_lower))
        for skill in unmatched_skills:
            # Check if any word is a close typo to this skill
            match = process.extractOne(skill, words, scorer=fuzz.ratio)
            if match and match[1] >= fuzzy_cutoff:
                detected_skills.add(skill)

    return sorted(list(detected_skills))


def extract_years_experience(text: str) -> float:
    """
    Parses mentions of years of experience using regular expressions.
    Examples matched: '3 years', '2.5+ yrs experience', '5 yr', '4+ years'
    """
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:\+?\s*)?(?:years?|yrs?|y)\s+(?:of\s+)?experience',
        r'experience\s*(?:of\s*)?:?\s*(\d+(?:\.\d+)?)\s*(?:\+?\s*)?(?:years?|yrs?)',
        r'(\d+(?:\.\d+)?)\s*(?:\+?\s*)?(?:years?|yrs?)\b'
    ]
    
    max_years = 0.0
    text_lower = text.lower()
    for pat in patterns:
        for m in re.finditer(pat, text_lower):
            try:
                val = float(m.group(1))
                # Discard unrealistic numbers like year numbers '2021'
                if 0.5 <= val <= 35.0:
                    max_years = max(max_years, val)
            except ValueError:
                continue
                
    return max_years


def extract_education(text: str) -> List[str]:
    """Extracts degree levels and qualifications."""
    degrees = []
    text_lower = text.lower()
    
    degree_keywords = {
        "Ph.D / Doctorate": [r'\bph\.?d\b', r'\bdoctorate\b'],
        "Master's Degree (M.Tech/MS/MCA)": [r'\bm\.?tech\b', r'\bm\.?s\b', r'\bmca\b', r'\bmaster\b'],
        "Bachelor's Degree (B.Tech/BE/BCA/BS)": [r'\bb\.?tech\b', r'\bb\.?e\b', r'\bbca\b', r'\bb\.?s\b', r'\bbachelor\b'],
        "Diploma": [r'\bdiploma\b']
    }
    
    for degree_name, patterns in degree_keywords.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                degrees.append(degree_name)
                break
                
    return degrees or ["Not Specified"]


def analyze_skill_gaps(candidate_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
    """
    Identifies matched skills and missing must-have gaps.
    """
    cand_set = set(s.lower() for s in candidate_skills)
    req_set = set(s.lower() for s in required_skills)
    
    matched = sorted(list(cand_set.intersection(req_set)))
    missing = sorted(list(req_set - cand_set))
    match_ratio = len(matched) / max(1, len(req_set))
    
    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_ratio": round(match_ratio, 3),
        "total_required": len(req_set),
        "total_matched": len(matched)
    }


def extract_jd_requirements(jd_text: str, taxonomy_path: Optional[str | Path] = None) -> Dict[str, Any]:
    """
    Parses Job Description into Must-Have and Nice-to-Have skill sets.
    """
    text_lower = jd_text.lower()
    must_have = []
    nice_to_have = []
    
    # Split text if Must-Have or Nice-to-Have sections exist
    must_match = re.search(r'(?:must[- ]have|required skills?|minimum requirements?)(.*?)(?:nice[- ]to[- ]have|preferred|good to have|responsibilities|$)', text_lower, re.DOTALL)
    nice_match = re.search(r'(?:nice[- ]to[- ]have|preferred|good to have)(.*?)(?:responsibilities|requirements|$)', text_lower, re.DOTALL)
    
    if must_match:
        must_have = extract_skills(must_match.group(1), taxonomy_path)
    if nice_match:
        nice_to_have = extract_skills(nice_match.group(1), taxonomy_path)
        
    # If no explicit sections found, extract all skills as core
    all_skills = extract_skills(jd_text, taxonomy_path)
    if not must_have:
        must_have = all_skills[:6] if len(all_skills) >= 6 else all_skills
        nice_to_have = all_skills[6:] if len(all_skills) >= 6 else []
        
    return {
        "must_have": must_have,
        "nice_to_have": nice_to_have,
        "all_skills": all_skills
    }

