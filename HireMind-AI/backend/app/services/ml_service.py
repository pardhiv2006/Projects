import os
import joblib  # type: ignore[import-untyped]
import numpy as np  # type: ignore[import-untyped]
from typing import Dict, List, Optional
from app.core.config import settings

_model = None
_vectorizer = None
_label_encoder = None

DOMAIN_SKILLS = {
    "Data Science": ["python", "machine learning", "deep learning", "pandas", "numpy", "tensorflow",
                     "pytorch", "scikit-learn", "data analysis", "statistics", "sql", "nlp"],
    "Web Development": ["react", "javascript", "html", "css", "node.js", "typescript", "angular",
                        "vue", "next.js", "rest api", "graphql", "bootstrap", "tailwind"],
    "DevOps": ["docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "terraform", "ansible",
               "jenkins", "linux", "bash", "github actions", "monitoring"],
    "AI Engineer": ["machine learning", "deep learning", "nlp", "computer vision", "pytorch",
                    "tensorflow", "transformers", "llm", "python", "cuda", "model deployment"],
    "Mobile Development": ["android", "ios", "react native", "flutter", "dart", "kotlin", "swift",
                           "mobile ui", "firebase", "push notifications"],
    "Backend Development": ["python", "java", "go", "node.js", "fastapi", "django", "spring boot",
                            "postgresql", "redis", "microservices", "rest api", "docker"],
    "Cybersecurity": ["penetration testing", "network security", "ethical hacking", "siem",
                      "vulnerability", "firewall", "linux", "python", "cryptography"],
    "Cloud Engineering": ["aws", "azure", "gcp", "terraform", "kubernetes", "docker", "cloud",
                          "serverless", "lambda", "s3", "ec2", "iam"],
}

def _preprocess_text(text: str) -> str:
    """Internal helper to match train_model.py preprocessing."""
    import re
    if not isinstance(text, str): return ""
    text = re.sub(r'http\S+\s*', ' ', text)
    text = re.sub(r'RT|cc', ' ', text)
    text = re.sub(r'#\S+', '', text)
    text = re.sub(r'@\S+', '  ', text)
    text = re.sub(r'[%s]' % re.escape(r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', text)
    text = re.sub(r'[^\x00-\x7f]', r' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()

def _map_role_to_domain(role: str) -> str:
    """Map specific roles from the 3000-resume dataset to high-level platform domains."""
    role_lower = role.lower()
    mapping = {
        "Data Science": ["data", "scientist", "analyst", "statistician", "mathematics"],
        "Web Development": ["web", "front", "ui", "react", "angular", "javascript", "php", "html", "css"],
        "DevOps": ["devops", "release", "build", "jenkins", "docker", "kubernetes", "automation"],
        "AI Engineer": ["ml", "machine learning", "ai", "nlp", "vision", "generative"],
        "Mobile Development": ["android", "ios", "iphone", "mobile", "flutter", "kotlin", "swift"],
        "Backend Development": ["java", "python", "backend", "j2ee", "spring", "django", "node", "go"],
        "Cybersecurity": ["security", "cyber", "penetration", "ethical", "siem", "firewall"],
        "Cloud Engineering": ["cloud", "azure", "gcp", "terraform", "cloud", "architect"],
    }
    for domain, keywords in mapping.items():
        if any(kw in role_lower for kw in keywords):
            return domain
    
    # Fallback mappings for common roles in the dataset
    if "oracle" in role_lower or "db" in role_lower or "sql" in role_lower: return "Backend Development"
    if "sap" in role_lower: return "Cloud Engineering"
    if "qa" in role_lower or "test" in role_lower: return "DevOps"
    if "consultant" in role_lower or "manager" in role_lower or "analyst" in role_lower: return "Data Science"
    
    return "Web Development" # Default

def _load_models():
    global _model, _vectorizer, _label_encoder
    try:
        # Load from new artifacts folder
        m_path = os.path.join(os.getcwd(), settings.ML_MODEL_PATH)
        v_path = os.path.join(os.getcwd(), settings.VECTORIZER_PATH)
        l_path = os.path.join(os.getcwd(), settings.LABEL_ENCODER_PATH)
        
        if os.path.exists(m_path):
            _model = joblib.load(m_path)
            _vectorizer = joblib.load(v_path)
            _label_encoder = joblib.load(l_path)
            print(f"✅ ML Service: SVM Role Classifier loaded from {m_path}")
            return True
    except Exception as e:
        print(f"⚠️ ML Service: Failed to load models: {e}")
    return False

def predict_domain(raw_text: str, skills: List[str]) -> Dict:
    """Predict resume domain using trained SVM model with high-level mapping."""
    global _model, _vectorizer, _label_encoder

    if _model is None:
        _load_models()

    combined_text = raw_text + " " + " ".join(skills)
    cleaned_text = _preprocess_text(combined_text)

    # Try ML model first
    if _model and _vectorizer and _label_encoder:
        try:
            vec = _vectorizer.transform([cleaned_text])
            
            # LinearSVC decision scores
            if hasattr(_model, "decision_function"):
                scores = _model.decision_function(vec)[0]
                # Manual softmax for confidence percentage
                exp_scores = np.exp(scores - np.max(scores))
                probs = exp_scores / np.sum(exp_scores)
            else:
                probs = _model.predict_proba(vec)[0]
            
            classes = _label_encoder.classes_
            idx = np.argmax(probs)
            predicted_role = classes[idx]
            confidence = float(round(probs[idx] * 100, 2))
            
            # Map granular role to platform domain
            predicted_domain = _map_role_to_domain(predicted_role)
            
            # For "all_predictions", we'll just show the high-level domain scores for UI
            all_preds = {predicted_domain: confidence}
            
            return {
                "predicted_domain": predicted_domain,
                "confidence_score": confidence,
                "all_predictions": all_preds,
                "specific_role": predicted_role
            }
        except Exception as e:
            print(f"⚠️ Prediction error: {e}")
            pass

    # Rule-based fallback
    combined_lower = cleaned_text.lower()
    scores = {}
    for domain, keywords in DOMAIN_SKILLS.items():
        score = sum(1 for kw in keywords if kw.lower() in combined_lower)
        scores[domain] = round((score / len(keywords)) * 100, 2)

    best = max(scores, key=scores.get) if any(scores.values()) else "Web Development"
    return {
        "predicted_domain": best,
        "confidence_score": scores.get(best, 40.0),
        "all_predictions": scores,
    }


def compute_match_score(resume_text: str, job_description: str, job_skills: str) -> Dict:
    """Compute semantic similarity between resume and job using sentence-transformers."""
    try:
        from sentence_transformers import SentenceTransformer, util
        model = SentenceTransformer("all-MiniLM-L6-v2")
        emb1 = model.encode(resume_text[:2000], convert_to_tensor=True)
        emb2 = model.encode(job_description[:2000] + " " + job_skills, convert_to_tensor=True)
        similarity = float(util.cos_sim(emb1, emb2)[0][0])
        score = round(min(similarity * 140, 99.0), 2)  # scale to 0-99
    except Exception:
        # Jaccard fallback
        resume_words = set(resume_text.lower().split())
        job_words = set((job_description + " " + job_skills).lower().split())
        intersection = resume_words & job_words
        union = resume_words | job_words
        score = round((len(intersection) / max(len(union), 1)) * 100, 2)

    return {"match_score": max(score, 5.0)}


def find_missing_skills(resume_skills: List[str], job_skills_str: str) -> List[str]:
    """Find skills in job description not present in resume."""
    resume_lower = {s.lower() for s in resume_skills}
    job_skill_list = [s.strip() for s in job_skills_str.split(",") if s.strip()]
    missing = [s for s in job_skill_list if s.lower() not in resume_lower]
    return missing[:8]


def generate_ai_feedback(skills: List[str], parsed_data: dict, match_score: float) -> Dict:
    """Generate actionable AI resume feedback."""
    feedback = []
    suggestions = []

    if len(skills) < 5:
        suggestions.append("Add more technical skills relevant to your target role.")
    if not parsed_data.get("projects"):
        suggestions.append("Include at least 2-3 projects with GitHub links and outcomes.")
    if not parsed_data.get("certifications"):
        suggestions.append("Add industry certifications (AWS, Google, Coursera) to strengthen your profile.")
    if not parsed_data.get("experience"):
        suggestions.append("Highlight measurable achievements (e.g., 'Reduced latency by 40%').")
    if match_score < 50:
        suggestions.append("Tailor your resume keywords to match the job description more closely.")
    if match_score >= 75:
        feedback.append("Strong profile match! Focus on interview preparation.")

    return {
        "score": match_score,
        "strengths": [f"Strong in: {', '.join(skills[:4])}"] if skills else [],
        "improvements": suggestions or ["Your resume looks great! Minor polish recommended."],
        "overall": "Excellent" if match_score >= 80 else "Good" if match_score >= 60 else "Needs Improvement",
    }


def generate_interview_questions(domain: str, skills: List[str], job_title: str) -> Dict:
    """Generate domain-specific interview questions."""
    questions = {
        "technical": [],
        "hr": [
            "Tell me about yourself and your career goals.",
            "Where do you see yourself in 5 years?",
            "Describe a challenging project and how you handled it.",
            "What motivates you to apply for this role?",
            "How do you handle tight deadlines and pressure?",
        ],
        "role_specific": [],
    }

    domain_questions = {
        "Data Science": [
            "Explain the bias-variance tradeoff.",
            "How do you handle class imbalance in datasets?",
            "What is regularization and when would you use L1 vs L2?",
            "Describe the end-to-end ML pipeline you've worked on.",
            "How do you evaluate a classification model beyond accuracy?",
        ],
        "Web Development": [
            "Explain the virtual DOM and how React uses it.",
            "What is the difference between SSR, CSR, and SSG?",
            "How do you optimize web application performance?",
            "Explain CORS and how you handle it in APIs.",
            "Describe RESTful API design principles.",
        ],
        "DevOps": [
            "Explain the CI/CD pipeline you've implemented.",
            "What is the difference between Docker and Kubernetes?",
            "How do you handle secrets management in cloud?",
            "Describe blue-green deployment strategy.",
            "How do you monitor application health in production?",
        ],
        "AI Engineer": [
            "What is the attention mechanism in transformers?",
            "How do you fine-tune a pre-trained LLM?",
            "Explain RAG (Retrieval-Augmented Generation).",
            "How do you evaluate NLP model performance?",
            "Describe challenges in deploying ML models to production.",
        ],
        "Mobile Development": [
            "How do you manage state in Flutter/React Native?",
            "Explain the difference between native and hybrid apps.",
            "How do you handle offline functionality in mobile apps?",
            "Describe push notification implementation.",
            "How do you optimize app performance for low-end devices?",
        ],
        "Backend Development": [
            "How do you design a scalable REST API?",
            "Explain database indexing and when to use it.",
            "What is the N+1 query problem and how do you solve it?",
            "Describe microservices vs monolithic architecture.",
            "How do you handle authentication and authorization?",
        ],
    }

    questions["technical"] = domain_questions.get(domain, [
        f"Explain your experience with {skills[0] if skills else 'your primary technology'}.",
        "What design patterns have you implemented?",
        "How do you approach code reviews?",
        "Describe your testing strategy.",
        "How do you stay updated with new technologies?",
    ])

    questions["role_specific"] = [
        f"What relevant experience do you have for {job_title}?",
        f"Describe a {job_title} project that you're most proud of.",
        f"What tools do you use daily as a {job_title}?",
    ]

    return questions
