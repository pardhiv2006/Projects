import re
import io
from typing import Dict, Any, List

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using pdfplumber."""
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        # Fallback to PyMuPDF
        try:
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            return text.strip()
        except Exception:
            return ""

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    except Exception:
        return ""

# ── Skill Keywords DB ────────────────────────────────────────────────
TECH_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "kotlin", "swift",
    "react", "next.js", "vue", "angular", "html", "css", "tailwind", "bootstrap",
    "node.js", "express", "fastapi", "flask", "django", "spring boot", "laravel",
    "postgresql", "mysql", "mongodb", "redis", "sqlite", "elasticsearch",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
    "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn",
    "git", "github", "gitlab", "ci/cd", "jenkins", "github actions",
    "rest api", "graphql", "microservices", "sql", "nosql",
    "linux", "bash", "powershell", "agile", "scrum", "jira",
    "data analysis", "data visualization", "tableau", "power bi",
    "hadoop", "spark", "kafka", "airflow", "dbt",
    "selenium", "pytest", "junit", "cypress", "jest",
    "figma", "adobe xd", "ui/ux", "responsive design",
    "blockchain", "solidity", "smart contracts",
    "dart", "flutter", "react native", "android", "ios",
]

def extract_skills(text: str) -> List[str]:
    text_lower = text.lower()
    found = []
    for skill in TECH_SKILLS:
        if skill in text_lower:
            found.append(skill.title() if len(skill) > 3 else skill.upper())
    return list(set(found))

def extract_education(text: str) -> List[Dict[str, str]]:
    education = []
    edu_keywords = ["b.tech", "b.e", "m.tech", "mba", "bsc", "msc", "phd", "bachelor", "master",
                    "degree", "university", "college", "institute", "school", "diploma"]
    lines = text.split("\n")
    for line in lines:
        if any(kw in line.lower() for kw in edu_keywords):
            cleaned = line.strip()
            if len(cleaned) > 10:
                education.append({"text": cleaned})
    return education[:5]

def extract_experience(text: str) -> List[Dict[str, str]]:
    experience = []
    exp_keywords = ["intern", "engineer", "developer", "analyst", "manager", "architect",
                    "lead", "senior", "junior", "associate", "consultant", "specialist"]
    lines = text.split("\n")
    for line in lines:
        if any(kw in line.lower() for kw in exp_keywords):
            cleaned = line.strip()
            if len(cleaned) > 15:
                experience.append({"text": cleaned})
    return experience[:8]

def extract_projects(text: str) -> List[Dict[str, str]]:
    projects = []
    proj_keywords = ["project", "built", "developed", "created", "implemented", "designed",
                     "deployed", "integrated", "automated"]
    lines = text.split("\n")
    for line in lines:
        if any(kw in line.lower() for kw in proj_keywords):
            cleaned = line.strip()
            if len(cleaned) > 20:
                projects.append({"text": cleaned})
    return projects[:6]

def extract_certifications(text: str) -> List[str]:
    certs = []
    cert_keywords = ["certified", "certification", "aws certified", "google certified",
                     "microsoft certified", "oracle certified", "coursera", "udemy", "edx"]
    lines = text.split("\n")
    for line in lines:
        if any(kw in line.lower() for kw in cert_keywords):
            cleaned = line.strip()
            if len(cleaned) > 10:
                certs.append(cleaned)
    return certs[:5]

def parse_resume(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Main entry point: parse resume file and return structured data."""
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        raw_text = extract_text_from_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        raw_text = extract_text_from_docx(file_bytes)
    else:
        raw_text = ""

    return {
        "raw_text": raw_text,
        "skills": extract_skills(raw_text),
        "education": extract_education(raw_text),
        "experience": extract_experience(raw_text),
        "projects": extract_projects(raw_text),
        "certifications": extract_certifications(raw_text),
    }
