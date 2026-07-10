from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas.chat import ChatRequest, ChatResponse, SourceItem
# from backend.services.retrieval_service import retrieve
from backend.core.config import ALLOWED_ORIGINS, DEFAULT_TOP_K
from backend.services.llm_service import generate_answer, generate_web_verified_answer
from backend.services.router_service import route_query, debug_route_query
from backend.services.verification_service import search_web_tavily, filter_web_results
from backend.services.file_service import save_uploaded_file
from backend.services.upload_service import (
    index_uploaded_file, 
    list_uploaded_files, 
    delete_uploaded_file
)
from backend.services.retrieval_service import (
    retrieve_faq,
    retrieve_mandai,
    retrieve_hybrid,
    retrieve_uploaded,
)

app = FastAPI(title="RAG Agent Chatbot for Mandai Wildlife Group", version="1.0.0")


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
    top_k = DEFAULT_TOP_K
    route_info = route_query(request.message)
    route = route_info["final_route"]

    if route == "faq":
        retrieved = retrieve_faq(request.message, top_k)
        answer = generate_answer(request.message, retrieved)

    elif route == "mandai":
        retrieved = retrieve_mandai(request.message, top_k)
        answer = generate_answer(request.message, retrieved)

    elif route == "uploaded_file":
        retrieved = retrieve_uploaded(request.message, top_k)
        if not retrieved:
            answer = "I could not find relevant information in the uploaded files."
        else:
            answer = generate_answer(request.message, retrieved)

    elif route == "verify_web":
        retrieved = search_web_tavily(request.message)
        retrieved = filter_web_results(retrieved)
        answer = generate_web_verified_answer(request.message, retrieved)

    else:
        retrieved = retrieve_hybrid(request.message, top_k)
        answer = generate_answer(request.message, retrieved)

    return ChatResponse(
        answer=answer,
        route=route,
        sources=[SourceItem(**item) for item in retrieved]
    )

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        saved = save_uploaded_file(file)
        indexed = index_uploaded_file(
            file_id=saved["file_id"],
            file_name=saved["file_name"],
            file_path=saved["file_path"],
        )
        return {
            "status": "indexed",
            "file_id": indexed["file_id"],
            "file_name": indexed["file_name"],
            "chunks_indexed": indexed["chunks_indexed"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
@app.get("/uploads")
def get_uploads():
    return {"files": list_uploaded_files()}

@app.delete("/uploads/{file_id}")
def remove_upload(file_id: str):
    result = delete_uploaded_file(file_id)

    if not result["deleted"]:
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    return result