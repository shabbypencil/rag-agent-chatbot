from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas.chat import ChatRequest, ChatResponse

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
    return ChatResponse(
        answer = f"Received message: {request.message}",
        route = "placeholder",
        sources = []
    )
