from pathlib import Path
from backend.core.config import (
    UPLOADS_COLLECTION,
    UPLOADS_DIR,
    INGESTION_CHUNK_SIZE,
    INGESTION_OVERLAP,
)
from backend.db.chroma_client import get_or_create_collection

def read_text_file(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8")

def chunk_text(text: str, chunk_size: int = INGESTION_CHUNK_SIZE, overlap: int = INGESTION_OVERLAP) -> list[str]:
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    step = max(1, chunk_size - overlap)

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks

def index_uploaded_file(file_id: str, file_name: str, file_path: str) -> dict:
    text = read_text_file(file_path)
    chunks = chunk_text(text)

    if not chunks:
        return {
            "file_id": file_id,
            "file_name": file_name,
            "chunks_indexed": 0,
        }

    collection = get_or_create_collection(UPLOADS_COLLECTION)

    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        chunk_id = f"{file_id}_chunk_{i}"
        ids.append(chunk_id)
        documents.append(chunk)
        metadatas.append({
            "file_id": file_id,
            "file_name": file_name,
            "source_type": "uploaded_file",
            "chunk_index": i,
        })

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    return {
        "file_id": file_id,
        "file_name": file_name,
        "chunks_indexed": len(chunks),
    }

def delete_uploaded_file(file_id: str):
    collection = get_or_create_collection(UPLOADS_COLLECTION)

    results = collection.get(where={"file_id": file_id})
    ids = results.get("ids", [])

    if not ids:
        return {"deleted": False, "reason": "file not found"}

    metadatas = results.get("metadatas", [])
    file_name = None
    if metadatas:
        file_name = metadatas[0].get("file_name")

    collection.delete(where={"file_id": file_id})

    if file_name:
        file_path = Path(UPLOADS_DIR) / file_name
        if file_path.exists():
            file_path.unlink()

    return {
        "deleted": True,
        "file_id": file_id,
        "file_name": file_name,
        "chunks_deleted": len(ids),
    }

def list_uploaded_files():
    collection = get_or_create_collection(UPLOADS_COLLECTION)
    results = collection.get(include=["metadatas"])

    seen = {}
    for meta in results.get("metadatas", []):
        file_id = meta.get("file_id")
        file_name = meta.get("file_name")
        if file_id and file_id not in seen:
            seen[file_id] = {
                "file_id": file_id,
                "file_name": file_name,
            }

    return list(seen.values())