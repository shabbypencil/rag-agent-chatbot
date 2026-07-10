# rag-agent-chatbot

An AI agent chatbot built with FastAPI and Streamlit that uses retrieval-augmented generation (RAG) to answer user questions from multiple knowledge sources.

## Features

- Semantic search over indexed knowledge sources.
- Context-aware question answering using retrieved chunks.
- Query routing across multiple sources such as FAQ, Mandai animal data, hybrid retrieval, uploaded files, and web verification.
- Internet verification for current or official information.
- File upload and indexing for user-provided `.txt` documents.
- FastAPI backend service.
- Streamlit frontend interface.

## Agentic functions

This chatbot currently demonstrates multiple agentic capabilities:

1. **Query routing**: routes user questions to the most appropriate source (`faq`, `mandai`, `hybrid`, `uploaded_file`, or `verify_web`).
2. **Web verification**: searches the web for latest or official information when the user asks for current or verified answers.
3. **File upload and storage**: allows users to upload `.txt` files, stores them locally, indexes them into Chroma, and answers questions from those uploaded documents.

## Project structure

```text
rag-agent-chatbot/
├── backend/
│   ├── core/
│   ├── db/
│   ├── ingestion/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── frontend/
│   └── app.py
├── data/
│   ├── raw/
│   │   ├── faq/
│   │   └── mandai/
│   ├── uploads/
│   └── chroma/
├── requirements.txt
└── README.md
```

## Tech stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Vector store**: ChromaDB (persistent local storage)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **LLM**: DeepSeek API
- **Web verification**: Tavily

## Prerequisites

1. Create and activate a virtual environment.

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Set up environment variables in a `.env` file.

Example:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
TAVILY_API_KEY=your_tavily_api_key
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
FAQ_COLLECTION=faq_collection
MANDAI_COLLECTION=mandai_collection
UPLOADS_COLLECTION=uploads_collection
DEFAULT_TOP_K=8
ALLOWED_ORIGINS=http://localhost:8501
```

4. Index the base knowledge sources before running the app.

```bash
python -m backend.ingestion.run_index
```

## Run locally

From the project root, start the backend first.

### Backend

```bash
uvicorn backend.main:app --reload
```

### Frontend

In a separate terminal:

```bash
streamlit run frontend/app.py
```

Then open:

[http://localhost:8501](http://localhost:8501)

## Supported routes

The chatbot currently supports these internal routes:

- `faq` - visitor information such as tickets, opening hours, facilities, accessibility, and policies.
- `mandai` - animal facts, park content, and Mandai-specific shows or attractions.
- `hybrid` - mixed queries that require more than one internal knowledge source.
- `uploaded_file` - questions explicitly referring to a user-uploaded document.
- `verify_web` - latest, current, official, or externally verified information.

## Example test queries

### FAQ

- `What are the opening hours?`
- `Are lockers available?`
- `Can I buy tickets online?`

### Mandai

- `Tell me about the white tiger.`
- `What shows are at Bird Paradise?`
- `What can you tell me about the clouded leopard?`

### Hybrid

- `Can I see white tigers and do I need to book anything?`

### Web verification

- `What are the latest news of animal births at Mandai Wildlife Reserve?`
- `Verify the current opening hours of Mandai Wildlife Reserve.`

### Uploaded file
You may upload the files inside data/upload_test via the frontend to test this functionality

Uploaded files are:
- stored locally in `data/uploads/`
- chunked and indexed into `uploads_collection`
- retrievable when the user asks a question that explicitly refers to the uploaded document

Example prompts:
- `Based on my uploaded file, tell me some animal facts.`
- `According to my uploaded file, which animal can regenerate limbs?`
- `What animals are mentioned in the file I uploaded?`
- `Summarize the uploaded document.`

## Routing test script

To test the router logic directly from the project root:

```bash
python -m backend.services.router_service
```

## Notes

- Uploaded files are separate from the built-in FAQ and Mandai datasets.
- Deleting a file from `data/uploads/` alone does not remove its indexed chunks from Chroma.
- Chroma data is persisted locally in `data/chroma/`.