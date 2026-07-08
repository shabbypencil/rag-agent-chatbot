from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CHROMA_DIR = DATA_DIR / "chroma"

FAQ_DIR = RAW_DIR / "faq"
MANDAI_DIR = RAW_DIR / "mandai"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
FAQ_COLLECTION = "faq_collection"
MANDAI_COLLECTION = "mandai_collection"