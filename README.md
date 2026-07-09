# rag-agent-chatbot
A simple RAG-based chatbot that retrieves relevant documentation content and answers user questions.

## Features
1. Semantic search over documentation
2. Context-aware question answering
3. FastAPI backend service
4. Streamlit frontend interface

## Prerequisites
1. python -m venv venv
2. venv\Scripts\Activate (Windows) or `source venv/bin/activate` (macOS/Linux)
3. pip install -r requirements.txt

## Run locally
From the project root:

Backend:
uvicorn backend.main:app --reload

Frontend:
streamlit run frontend/app.py

Open the app in your browser:
http://localhost:8501