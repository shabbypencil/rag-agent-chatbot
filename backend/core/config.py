from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CHROMA_DIR = DATA_DIR / "chroma"
FAQ_DIR = RAW_DIR / "faq"
MANDAI_DIR = RAW_DIR / "mandai"
UPLOADS_DIR = DATA_DIR / "uploads"

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE_URL = os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
FAQ_COLLECTION = os.getenv("FAQ_COLLECTION", "faq_collection")
MANDAI_COLLECTION = os.getenv("MANDAI_COLLECTION", "mandai_collection")
UPLOADS_COLLECTION = os.getenv("UPLOADS_COLLECTION", "uploads_collection")
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "4"))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(",")