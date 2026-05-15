import joblib
import os
import re

# ── Setup Paths ───────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

# Load artifacts
try:
    model = joblib.load(os.path.join(MODEL_DIR, "model.pkl"))
    vectorizer = joblib.load(os.path.join(MODEL_DIR, "vectorizer.pkl"))
    label_encoder = joblib.load(os.path.join(MODEL_DIR, "label_encoder.pkl"))
    print("✅ Model artifacts loaded successfully.")
except Exception as e:
    print(f"❌ Error loading model: {e}")

def preprocess_text(text):
    """Clean raw resume text for prediction."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'http\S+\s*', ' ', text)
    text = re.sub(r'RT|cc', ' ', text)
    text = re.sub(r'#\S+', '', text)
    text = re.sub(r'@\S+', '  ', text)
    text = re.sub(r'[%s]' % re.escape(r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', text)
    text = re.sub(r'[^\x00-\x7f]', r' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()

def predict_job_role(resume_text):
    """Predict the job role from raw resume text."""
    # Preprocess
    cleaned = preprocess_text(resume_text)
    
    # Vectorize
    vec = vectorizer.transform([cleaned])
    
    # Predict
    pred_label = model.predict(vec)[0]
    
    # Inverse transform to get role name
    role_name = label_encoder.inverse_transform([pred_label])[0]
    
    return role_name

if __name__ == "__main__":
    # Test cases
    test_resumes = [
        "Experienced Python developer with skills in Flask, Django, and PostgreSQL.",
        "Data Scientist with expertise in Machine Learning, Pandas, and Scikit-learn.",
        "React developer with experience in building responsive web applications.",
    ]
    
    for r in test_resumes:
        prediction = predict_job_role(r)
        print(f"\nResume snippet: {r[:50]}...")
        print(f"Predicted Role: {prediction}")
        print("-" * 30)
