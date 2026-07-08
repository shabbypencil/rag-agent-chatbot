from pathlib import Path

def load_text_files(folder: Path):
    documents = []
    for path in folder.glob("*"):
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            text = path.read_text(encoding="utf-8")
            documents.append({
                "doc_id": path.stem,
                "file_name": path.name,
                "text": text
            })
    return documents