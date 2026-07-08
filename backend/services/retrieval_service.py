from backend.db.chroma_client import get_or_create_collection
from backend.core.config import FAQ_COLLECTION, MANDAI_COLLECTION

def query_collection(collection_name: str, query: str, top_k: int = 4):
    collection = get_or_create_collection(collection_name)
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
    )

