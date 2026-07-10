from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas.chat import ChatRequest, ChatResponse, SourceItem
# from backend.services.retrieval_service import retrieve
from backend.core.config import ALLOWED_ORIGINS, DEFAULT_TOP_K
from backend.services.llm_service import generate_answer
from backend.services.router_service import route_query, debug_route_query
from backend.services.retrieval_service import (
    retrieve_faq,
    retrieve_mandai,
    retrieve_hybrid,
)

app = FastAPI(title="RAG Agent Chatbot")


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # print("DEBUG DEFAULT_TOP_K =", DEFAULT_TOP_K)
    top_k = DEFAULT_TOP_K
    # print("DEBUG effective top_k =", top_k)
    # print("DEBUG ROUTER:", debug_route_query(request.message))
    route = route_query(request.message)

    if route == "faq":
        retrieved = retrieve_faq(request.message, top_k)
    elif route == "mandai":
        retrieved = retrieve_mandai(request.message, top_k)
    else:
        retrieved = retrieve_hybrid(request.message, top_k)

    answer = generate_answer(request.message, retrieved)

    return ChatResponse(
        answer=answer,
        route=route,
        sources=[SourceItem(**item) for item in retrieved]
    )