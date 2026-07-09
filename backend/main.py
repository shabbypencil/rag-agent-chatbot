from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas.chat import ChatRequest, ChatResponse, SourceItem
from backend.services.retrieval_service import retrieve
from backend.services.llm_service import generate_answer
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file  

app =FastAPI(title="RAG Agent Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    retrieved = retrieve(request.message, request.top_k)
    answer = generate_answer(request.message, retrieved)

    return ChatResponse(
        answer = answer,
        route = "core_rag",
        sources = [SourceItem(**item) for item in retrieved]
    )
