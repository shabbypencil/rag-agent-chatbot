from pathlib import Path

def load_text_files(folder: Path):
    documents = []
    for path in folder.glob("*"):
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            text = path.read_text(encoding="utf-8")
            print(f"DEBUG: loaded file={path} size={len(text)}")
            documents.append({
                "doc_id": path.stem,
                "file_name": path.name,
                "text": text
            })
    print(f"DEBUG: total_documents={len(documents)}")
    return documents