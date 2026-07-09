from backend.ingestion.loaders import load_text_files
from backend.ingestion.chunker import chunk_text
from backend.db.chroma_client import get_or_create_collection
from backend.core.config import FAQ_DIR, MANDAI_DIR, FAQ_COLLECTION, MANDAI_COLLECTION

def index_folder(folder, collection_name, source_type):
    print(f"Starting indexing folder: {folder} into collection: {collection_name} with source type: {source_type}")
    collection = get_or_create_collection(collection_name)
    documents = load_text_files(folder)
    print(f"Loaded {len(documents)} documents from {folder}")

    ids, texts, metadatas = [], [], []

    for doc in documents:
        chunks = chunk_text(doc["text"])
        print(f"Document {doc['doc_id']} ({doc['file_name']}) produced {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            ids.append(f"{doc['doc_id']}_{i}")
            texts.append(chunk)
            metadatas.append({
                "source_type": source_type,
                "file_name": doc["file_name"],
                "chunk_index": i
            })

    if ids:
        print(f"Upserting {len(ids)} chunks into collection: {collection_name}")
        collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        print(f"Completed upsert for collection: {collection_name}")
    else:
        print(f"No chunks to upsert for folder: {folder}")

def run_full_index():
    index_folder(FAQ_DIR, FAQ_COLLECTION, "faq")
    index_folder(MANDAI_DIR, MANDAI_COLLECTION, "mandai")