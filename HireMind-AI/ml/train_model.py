import os
import re
import joblib  # type: ignore[import-untyped]
import pandas as pd  # type: ignore[import-untyped]
from sklearn.model_selection import train_test_split  # type: ignore[import-untyped]
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore[import-untyped]
from sklearn.svm import LinearSVC  # type: ignore[import-untyped]
from sklearn.pipeline import Pipeline  # type: ignore[import-untyped]
from sklearn.metrics import classification_report, accuracy_score  # type: ignore[import-untyped]
from sklearn.preprocessing import LabelEncoder  # type: ignore[import-untyped]

# ── Setup Paths ───────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "backend/datasets/cleaned_resume_dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "backend/models")
os.makedirs(MODEL_DIR, exist_ok=True)

# ── Synthetic Fallback ───────────────────────────────────────────────
TRAINING_DATA = [
    ("python machine learning deep learning pandas numpy tensorflow pytorch scikit-learn data analysis statistics nlp computer vision regression classification clustering", "Data Science"),
    ("react javascript html css node.js typescript next.js angular vue tailwind bootstrap rest api graphql", "Web Development"),
    ("docker kubernetes terraform ansible jenkins github actions ci/cd linux bash aws azure gcp", "DevOps"),
    ("machine learning deep learning nlp computer vision pytorch tensorflow transformers llm python", "AI Engineer"),
    ("android ios react native flutter dart kotlin swift mobile ui firebase push notifications", "Mobile Development"),
    ("python java go node.js fastapi django spring boot postgresql redis microservices rest api docker", "Backend Development"),
    ("penetration testing network security ethical hacking siem vulnerability firewall linux python cryptography", "Cybersecurity"),
    ("aws azure gcp terraform kubernetes docker cloud serverless lambda s3 ec2 iam", "Cloud Engineering"),
]

def preprocess_text(text):
    """Clean raw resume text for NLP classification."""
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

def train():
    print("🚀 Initializing HireMind AI Model Trainer...")
    
    if os.path.exists(DATASET_PATH):
        print(f"📊 Loading dataset from {DATASET_PATH}...")
        df = pd.read_csv(DATASET_PATH)  # type: ignore
        
        if 'cleaned_text' not in df.columns and 'Text' in df.columns:
            df['cleaned_text'] = df['Text']
        elif 'cleaned_text' not in df.columns:
            df['cleaned_text'] = df.iloc[:, -1]

        # Filter rare job titles (min 10 samples)
        counts = df['job_title'].value_counts()
        df = df[df['job_title'].isin(counts[counts >= 10].index)]  # type: ignore
        
        X = df['cleaned_text'].apply(preprocess_text)  # type: ignore
        y_labels = df['job_title']
        print(f"✅ Loaded {len(df)} samples across {y_labels.nunique()} categories.")
    else:
        print("⚠️ Warning: CSV dataset not found. Falling back to synthetic neural data.")
        X = [preprocess_text(item[0]) for item in TRAINING_DATA]
        y_labels = [item[1] for item in TRAINING_DATA]

    # Label Encoding
    le = LabelEncoder()
    y = le.fit_transform(y_labels)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Training Pipeline
    print("🏗️ Building SVM Pipeline...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            sublinear_tf=True,
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )),
        ('clf', LinearSVC(C=1.0, random_state=42, max_iter=2000, dual="auto"))
    ])
    
    pipeline.fit(X_train, y_train)
    
    # Evaluation
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"✨ Model Accuracy: {acc:.2%}")
    
    # Persistence
    print(f"💾 Saving artifacts to {MODEL_DIR}...")
    joblib.dump(pipeline.named_steps['clf'], os.path.join(MODEL_DIR, "model.pkl"))  # type: ignore
    joblib.dump(pipeline.named_steps['tfidf'], os.path.join(MODEL_DIR, "vectorizer.pkl"))  # type: ignore
    joblib.dump(le, os.path.join(MODEL_DIR, "label_encoder.pkl"))  # type: ignore
    
    print("✅ Training complete! AI models synchronized.")

if __name__ == "__main__":
    train()

