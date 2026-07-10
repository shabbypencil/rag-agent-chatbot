from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()


# Define the base directory and various data directories
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CHROMA_DIR = DATA_DIR / "chroma"
FAQ_DIR = RAW_DIR / "faq"
MANDAI_DIR = RAW_DIR / "mandai"
UPLOADS_DIR = DATA_DIR / "uploads"

# Define ingestion and embedding parameters
INGESTION_CHUNK_SIZE = int(os.getenv("INGESTION_CHUNK_SIZE", "500"))
INGESTION_OVERLAP = int(os.getenv("INGESTION_OVERLAP", "50"))

# Define environment variables and default values
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE_URL = os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_MAX_RESULTS = int(os.getenv("TAVILY_MAX_RESULTS", "3"))
FAQ_COLLECTION = os.getenv("FAQ_COLLECTION", "faq_collection")
MANDAI_COLLECTION = os.getenv("MANDAI_COLLECTION", "mandai_collection")
UPLOADS_COLLECTION = os.getenv("UPLOADS_COLLECTION", "uploads_collection")
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "8"))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(",")