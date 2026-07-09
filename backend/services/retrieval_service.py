from backend.db.chroma_client import get_or_create_collection
from backend.core.config import (
    FAQ_COLLECTION,
    MANDAI_COLLECTION,
    DEFAULT_TOP_K,
)


def query_collection(collection_name: str, query: str, top_k: int = DEFAULT_TOP_K):
    collection = get_or_create_collection(collection_name)
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
    )

    items = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    for doc, meta, dist, doc_id in zip(docs, metas, distances, ids):
        items.append({
            "source_id": doc_id,
            "title": meta.get("file_name", "unknown"),
            "snippet": doc[:300],
            "distance": float(dist),
        })

    return items


def retrieve(query: str, top_k: int = DEFAULT_TOP_K):
    faq_results = query_collection(FAQ_COLLECTION, query, top_k)
    mandai_results = query_collection(MANDAI_COLLECTION, query, top_k)

    combined_results = faq_results + mandai_results
    combined_results.sort(key=lambda x: x["distance"])

    return combined_results[:top_k]