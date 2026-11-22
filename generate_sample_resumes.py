"""
Synthetic Resume Generator
Generates realistic multi-format (.pdf, .docx, .txt) sample resumes for simulation and testing.
"""
from pathlib import Path
from fpdf import FPDF
from docx import Document


def create_pdf_resume(filepath: Path, name: str, email: str, phone: str, summary: str, skills: list, exp: str, edu: str):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Header: Name
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, name, new_x="LMARGIN", new_y="NEXT", align="C")
    
    # Contact Info
    pdf.set_font("Helvetica", "", 10)
    contact_str = f"Email: {email} | Phone: {phone} | Location: Bangalore, India"
    pdf.cell(0, 6, contact_str, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    
    # Summary
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "PROFESSIONAL SUMMARY", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, summary)
    pdf.ln(4)
    
    # Skills
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "TECHNICAL SKILLS", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, ", ".join(skills))
    pdf.ln(4)
    
    # Experience
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "WORK EXPERIENCE", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, exp)
    pdf.ln(4)
    
    # Education
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "EDUCATION", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, edu)
    
    pdf.output(str(filepath))


def create_docx_resume(filepath: Path, name: str, email: str, phone: str, summary: str, skills: list, exp: str, edu: str):
    doc = Document()
    doc.add_heading(name, level=0)
    p_contact = doc.add_paragraph(f"Email: {email} | Phone: {phone} | Location: Pune, India")
    
    doc.add_heading("Professional Summary", level=1)
    doc.add_paragraph(summary)
    
    doc.add_heading("Technical Skills", level=1)
    doc.add_paragraph(", ".join(skills))
    
    doc.add_heading("Work Experience", level=1)
    doc.add_paragraph(exp)
    
    doc.add_heading("Education", level=1)
    doc.add_paragraph(edu)
    
    doc.save(str(filepath))


def create_txt_resume(filepath: Path, name: str, email: str, phone: str, summary: str, skills: list, exp: str, edu: str):
    content = f"""{name}
Email: {email} | Phone: {phone} | Location: Hyderabad, India

PROFESSIONAL SUMMARY
{summary}

TECHNICAL SKILLS
{", ".join(skills)}

WORK EXPERIENCE
{exp}

EDUCATION
{edu}
"""
    filepath.write_text(content, encoding="utf-8")


def generate_all_sample_resumes(output_dir: str = "resumes"):
    p_dir = Path(output_dir)
    p_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Aarav Sharma (Strong Match - PDF)
    create_pdf_resume(
        p_dir / "resume_aarav_sharma.pdf",
        name="Aarav Sharma",
        email="aarav.sharma@example.com",
        phone="+91 98765 43210",
        summary="Senior Python Developer and Data Engineer with 4.5 years of experience architecting automated data pipelines, ML workflows, and REST APIs. Expert in Python, SQL, Pandas, NumPy, Scikit-learn, and FastAPI.",
        skills=["Python", "Pandas", "NumPy", "Scikit-learn", "SQL", "PostgreSQL", "FastAPI", "Docker", "Git", "GitHub", "AWS", "REST API", "Linux"],
        exp="Software Engineer at TechCorp (4.5 years of experience):\n- Developed scalable ETL data pipelines handling 5M daily records using Python and Pandas.\n- Built high-throughput microservices using FastAPI and PostgreSQL with Docker.\n- Trained and deployed predictive machine learning models using Scikit-learn.",
        edu="B.Tech in Computer Science and Engineering, National Institute of Technology (NIT)"
    )
    
    # 2. Priya Patel (Strong Data Science Match - DOCX)
    create_docx_resume(
        p_dir / "resume_priya_patel.docx",
        name="Priya Patel",
        email="priya.patel@example.com",
        phone="+91 91234 56789",
        summary="Data Scientist with 3.2 years of professional experience in predictive modeling, statistical data analysis, and natural language processing. Skilled in Python, Scikit-learn, NumPy, Pandas, SQL, and Flask.",
        skills=["Python", "Data Science", "Machine Learning", "Scikit-learn", "Pandas", "NumPy", "SQL", "Flask", "NLP", "Git", "Power BI", "Tableau"],
        exp="Data Scientist at AnalyticsHub (3.2 years of experience):\n- Built NLP text classification and sentiment analysis models using Scikit-learn and TF-IDF.\n- Automated data extraction pipelines and generated business dashboards using Power BI and SQL.\n- Deployed production inference endpoints using Flask and Git CI/CD.",
        edu="M.Tech in Data Science & Artificial Intelligence, IIIT Bangalore"
    )
    
    # 3. Rohan Verma (Backend Engineer Match - PDF)
    create_pdf_resume(
        p_dir / "resume_rohan_verma.pdf",
        name="Rohan Verma",
        email="rohan.verma@example.com",
        phone="+91 98111 22334",
        summary="Backend Software Engineer with 2.5 years of experience developing RESTful APIs, microservices, and database systems using Python, Django, FastAPI, and Docker.",
        skills=["Python", "FastAPI", "Django", "SQL", "PostgreSQL", "Docker", "Git", "REST API", "Linux"],
        exp="Backend Developer at CloudScale Solutions (2.5 years of experience):\n- Designed REST APIs with FastAPI and Django serving 100K active users.\n- Optimized complex SQL queries in PostgreSQL reducing latency by 40%.\n- Containerized microservices using Docker and orchestrated deployments with Git workflows.",
        edu="B.Tech in Information Technology, Anna University"
    )
    
    # 4. Neha Gupta (Junior Analyst Match - TXT)
    create_txt_resume(
        p_dir / "resume_neha_gupta.txt",
        name="Neha Gupta",
        email="neha.gupta@example.com",
        phone="+91 97654 32109",
        summary="Junior Data Analyst with 1.5 years experience querying databases, preparing tabular reports, and performing exploratory data analysis using Python, Pandas, SQL, and Excel.",
        skills=["Python", "Pandas", "SQL", "Excel", "Power BI", "Data Analysis", "Git"],
        exp="Junior Analyst at FinTech Insights (1.5 years of experience):\n- Cleaned and transformed structured customer transactional data using Pandas and SQL.\n- Built weekly KPI summary dashboards in Power BI and MS Excel.",
        edu="BCA (Bachelor of Computer Applications), Delhi University"
    )
    
    # 5. Vikas Kumar (Completely Unrelated Sales Profile - PDF)
    create_pdf_resume(
        p_dir / "resume_vikas_kumar.pdf",
        name="Vikas Kumar",
        email="vikas.kumar@example.com",
        phone="+91 99887 76655",
        summary="Senior B2B Sales Executive and Account Manager with 5 years experience driving enterprise revenue, cold outreach, and client onboarding.",
        skills=["B2B Sales", "Client Negotiation", "Lead Generation", "CRM", "Salesforce", "Cold Calling", "Account Management"],
        exp="Sales Executive at RetailMax (5 years of experience):\n- Generated $1.2M in annual recurring revenue across enterprise accounts.\n- Managed CRM pipeline and customer meetings.",
        edu="B.Com (Bachelor of Commerce), Mumbai University"
    )
    
    # 6. Ananya Reddy (Frontend Developer Profile - DOCX)
    create_docx_resume(
        p_dir / "resume_ananya_reddy.docx",
        name="Ananya Reddy",
        email="ananya.reddy@example.com",
        phone="+91 93456 78901",
        summary="Frontend UI/UX Developer with 2 years of experience crafting interactive web applications using React, JavaScript, HTML, and CSS.",
        skills=["React", "JavaScript", "HTML", "CSS", "Node.js", "Git", "GitHub"],
        exp="Frontend Developer at WebDesign Studio (2 years of experience):\n- Built responsive user interfaces and web dashboards using React and Tailwind CSS.\n- Collaborated with product designers using Figma and Git version control.",
        edu="B.Tech in Computer Science, Osmania University"
    )
    
    print(f"[Success] Generated 6 multi-format sample resumes in '{output_dir}/'")


if __name__ == "__main__":
    generate_all_sample_resumes()
