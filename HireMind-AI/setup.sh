#!/bin/bash

# Setup script for HireMind AI Platform

echo "🚀 Starting HireMind AI Setup..."

# 1. Backend Setup
echo "📦 Setting up Backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2. Train ML Model
echo "🧠 Training AI Models..."
python3 ../ml/train_model.py

# 3. Frontend Setup
echo "🎨 Setting up Frontend..."
cd ../frontend
npm install

echo "✅ Setup Complete!"
echo ""
echo "🔥 To start the application:"
echo "1. Start Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "2. Start Frontend: cd frontend && npm run dev"
