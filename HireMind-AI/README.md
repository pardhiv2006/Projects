# HireMind AI — Enterprise AI Recruitment Platform

HireMind AI is a production-level, AI-powered recruitment and career recommendation platform. It features deep learning models for resume classification, semantic job matching, and automated candidate analytics.

## 🚀 Core Features

- **Dual Portals**: Separate, premium experiences for **Recruiters** and **Candidates**.
- **AI Resume Parser**: High-accuracy extraction of skills, education, and experience from PDF/DOCX.
- **ML Role Classifier**: A trained **Linear SVM** model that classifies resumes into 100+ granular job roles with domain mapping.
- **Semantic Matching**: Sentence Transformers calculate match scores based on resume context vs job description.
- **Analytics Dashboard**: Real-time insights into applicant pipelines, match distributions, and top-trending skills.
- **Interview Preparation**: AI-generated technical and behavioral questions tailored to specific roles and resumes.

## 🛠 Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Framer Motion, Recharts.
- **Backend**: FastAPI (Python), SQLAlchemy (SQLite/PostgreSQL), JWT Auth.
- **AI/ML**: Scikit-learn (SVM), Sentence Transformers, Joblib, pdfplumber.

---

## 🚦 Installation & Setup

Before running the application, you must initialize the environment and train the ML models:

```bash
# Run the root setup script
npm run setup
```
*This installs all dependencies for both frontend/backend and trains the ML classifier using the provided dataset.*

---

## 🏃 How to Run

### **Option A: Single Command (Recommended)**
Run both the backend and frontend simultaneously in one terminal window:

```bash
npm run dev
```
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000/docs`

---

### **Option B: Manual Execution (Separate Terminals)**
If you prefer to see logs separately or need more control:

#### **Terminal 1: Start Backend**
```bash
cd backend
./venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

#### **Terminal 2: Start Frontend**
```bash
cd frontend
npm run dev
```

---

## 📂 Project Structure

- `/frontend`: Next.js application with glassmorphic UI components.
- `/backend`: FastAPI server containing the core logic and API routes.
- `/backend/models`: Trained ML artifacts (`model.pkl`, `vectorizer.pkl`, etc.).
- `/backend/datasets`: Source data for ML training.
- `/ml`: Original training scripts and synthetic data generators.

## 🏷 Role Classification Model
The system uses a **Linear SVM** model trained on ~9,000 real-world resumes, achieving high accuracy in classifying candidates into technical domains. It automatically maps granular roles (e.g., "Sr. Java Developer") to high-level platform categories for consistent visualization.
