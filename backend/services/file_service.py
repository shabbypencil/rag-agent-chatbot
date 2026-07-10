from pathlib import Path
from uuid import uuid4
import shutil

from backend.core.config import UPLOADS_DIR

ALLOWED_UPLOAD_EXTENSIONS = {".txt"}

def ensure_upload_dir() -> None:
    Path(UPLOADS_DIR).mkdir(parents=True, exist_ok=True)

def save_uploaded_file(upload_file) -> dict:
    ensure_upload_dir()

    original_name = upload_file.filename or "uploaded_file.txt"
    suffix = Path(original_name).suffix.lower()

    if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}. Only .txt is allowed for now.")

    file_id = str(uuid4())
    safe_name = f"{file_id}_{Path(original_name).name}"
    file_path = Path(UPLOADS_DIR) / safe_name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return {
        "file_id": file_id,
        "file_name": original_name,
        "stored_name": safe_name,
        "file_path": str(file_path),
    }