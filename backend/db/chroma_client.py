import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from backend.core.config import CHROMA_DIR, EMBEDDING_MODEL

embedding_function = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)

client = chromadb.PersistentClient(path=str(CHROMA_DIR))

def get_or_create_collection(name: str):
    return client.get_or_create_collection(
        name=name, 
        embedding_function=embedding_function
    )

