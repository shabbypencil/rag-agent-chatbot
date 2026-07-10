from backend.core.config import (
    INGESTION_CHUNK_SIZE,
    INGESTION_OVERLAP
)

def chunk_text(text: str, chunk_size: int = INGESTION_CHUNK_SIZE, overlap: int = INGESTION_OVERLAP):
    text = text.strip()
    print(f"[chunk_text] Received text of length: {len(text)}")
    print(f"[chunk_text] chunk_size={chunk_size}, overlap={overlap}")
    if not text:
        print("[chunk_text] Empty text after stripping; returning []")
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        print(f"[chunk_text] Creating chunk from {start} to {end} (actual {len(chunk)})")
        chunks.append(chunk)
        start += chunk_size - overlap
    print(f"[chunk_text] Created total {len(chunks)} chunks")
    return chunks