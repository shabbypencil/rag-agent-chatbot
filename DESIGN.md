# DESIGN.md

## Overview

This project is a retrieval-augmented generation (RAG) chatbot built with a FastAPI backend and a Streamlit frontend. The system answers user questions by retrieving relevant context from multiple knowledge sources, then passing that retrieved context into a language model for response generation. The chatbot is designed to demonstrate agentic behavior through source routing, web verification, and uploaded-document retrieval.

The core idea is to avoid relying on the language model alone. Instead, the application first decides where a query should be answered from, retrieves relevant chunks from the appropriate source, and then instructs the model to answer only from the provided context.

## Architecture

The system is organized into a few main layers:

- **Frontend**: a Streamlit application that sends user queries and file uploads to the backend.
- **API layer**: a FastAPI application exposing routes such as `/chat`, `/upload`, and health checks.
- **Routing layer**: decides whether the query should go to FAQ, Mandai, hybrid retrieval, uploaded-file retrieval, or web verification.
- **Retrieval layer**: queries Chroma collections and returns the most relevant chunks.
- **LLM layer**: handles route classification fallback and final answer generation using DeepSeek.
- **Storage layer**: persists documents, embeddings, and uploaded files locally using the `data/` directory structure and Chroma persistent storage.

At a high level, the request flow is:

1. User submits a question from the frontend.
2. FastAPI receives the request through `/chat`.
3. `route_query()` selects the most appropriate route.
4. The backend retrieves relevant chunks from the selected source.
5. The retrieved chunks are formatted into a structured context block.
6. The language model generates an answer constrained to that context.
7. The API returns the answer, route, and supporting sources to the frontend.

The upload flow is similar but starts with a file instead of a question:

1. User uploads a `.txt` file from the frontend.
2. FastAPI receives the file through `/upload`.
3. The file is saved to `data/uploads/` and assigned a `file_id`.
4. The text is read, chunked, and indexed into the uploads collection with metadata such as `file_id`, `file_name`, and `source_type`.
5. Later, if the user explicitly refers to the uploaded document, the system routes the query to the uploaded-file retrieval path.

## Prompt engineering choices

Two prompt types are used in the system: a routing prompt and an answer-generation prompt.

### 1. Routing prompt

The routing classifier prompt is intentionally short and structured. It defines a fixed set of valid route labels and gives a concise description of each one. The prompt then forces the model to return only valid JSON in the shape:

```json
{"route": "", "reason": ""}
```

This design choice keeps the router predictable and easy to validate in code. It also makes failures easy to catch because invalid output can be rejected and defaulted to `hybrid`.

### 2. Answer-generation prompt

The answer-generation system prompt emphasizes four constraints:

- Answer only using retrieved context.
- Clearly say when the answer is not contained in the context.
- Keep the response concise and direct.
- Avoid dumping raw context back to the user.

This prompt was chosen to reduce hallucination. In a RAG system, the most important behavior is grounded answering rather than free-form generation, so the prompt explicitly narrows the model’s role to synthesis from retrieved evidence.

### 3. Low-temperature settings

The route classifier runs at a low temperature (`0.1`) and the answer generator also uses a relatively low temperature (`0.2`). These values were chosen to increase consistency, reduce randomness, and make evaluation easier during testing.

### 4. Fallback behavior

The system uses conservative failure handling:

- If route classification returns invalid JSON or an unsupported route, it defaults to `hybrid`.
- If answer generation fails, the system falls back to a snippet-based response using the top retrieved source.

This makes the chatbot more robust during demos and local testing.

## Routing strategy

The project uses a **hybrid routing strategy**: rule-based routing first, then LLM fallback only when needed.

### Rule-based routing

The router scores each query using weighted FAQ phrases/keywords and Mandai phrases/keywords. For example:

- FAQ terms include tickets, hours, lockers, parking, accessibility, bookings, and facilities.
- Mandai terms include animal names, park names, presentations, and species-related vocabulary.

There is also a dedicated set of verification keywords such as `latest`, `current`, `official`, `verified`, and `news`. If these appear in the query, the route is immediately set to `verify_web` with high confidence.

The rule-based router returns:

- a route,
- a confidence score,
- a reason,
- FAQ and Mandai scores.

This design makes the route choice interpretable and easy to debug.

### LLM fallback

If the rule-based result is uncertain, especially when the route is `hybrid` or confidence is below the threshold, the backend calls the LLM classifier for a second opinion.

This approach was chosen for two reasons:

1. **Efficiency**: obvious queries do not need an LLM call.
2. **Flexibility**: ambiguous natural-language questions still get semantic route classification.

### Supported route types

The implemented route set is:

- `faq`: visitor information such as opening hours, tickets, lockers, transport, accessibility, and policies.
- `mandai`: park-specific animal facts, presentations, and attraction content.
- `hybrid`: questions that combine more than one internal source.
- `verify_web`: queries asking for current, latest, official, or externally verified information.
- `uploaded_file`: queries that explicitly refer to a user-uploaded document.

The uploaded-file route was added to support one of the assignment’s agentic functions: uploading and retrieving from user-provided files.

## Chunking approach

The ingestion pipeline uses fixed-size chunking with overlap for uploaded documents and the indexed knowledge base. The relevant parameters are controlled through configuration:[5]

- `INGESTION_CHUNK_SIZE`, default `500`
- `INGESTION_OVERLAP`, default `50`

The uploaded-file chunking logic works by:

1. stripping the full text,
2. moving through the text with a step size of `chunk_size - overlap`,
3. extracting each window as a chunk,
4. ignoring empty chunks.

This overlapping sliding-window approach was chosen because it is simple, deterministic, and preserves some context continuity across chunk boundaries. Without overlap, important facts near the edge of a chunk might be separated from related sentences. With a 50-character overlap, adjacent chunks retain some shared context.

The trade-off is that fixed-size chunking is not semantically perfect. It may split in the middle of a sentence or bullet point. However, for a lightweight assignment project with short text files and relatively simple factual content, this method is practical and easy to explain.

## Embeddings

The system uses the `sentence-transformers/all-MiniLM-L6-v2` embedding model for all document collections.

This model was chosen because it is:

- lightweight,
- widely used in semantic search projects,
- fast enough for local experimentation,
- accurate enough for short factual text retrieval.

The embedding function is created once in the Chroma client module using `SentenceTransformerEmbeddingFunction`, and then reused whenever a collection is created or queried.

Using a single embedding model across FAQ, Mandai, and uploaded documents simplifies the system. It ensures that all indexed sources are embedded in a consistent vector space, which makes retrieval behavior easier to reason about.

## Vector storage

The project uses **ChromaDB** as the vector store with local persistent storage.

### Persistence model

The Chroma client is initialized as:

```python
client = chromadb.PersistentClient(path=str(CHROMA_DIR))
```

This means vector data is written to the local filesystem under `data/chroma/` and persists across application restarts.

### Collection design

The system separates knowledge into multiple collections:

- `faq_collection`
- `mandai_collection`
- `uploads_collection`

This separation is important for routing. Instead of searching one large mixed store, the system can explicitly query the source that matches the route, which improves controllability and makes results easier to inspect.

### Retrieval behavior

The retrieval layer wraps collection querying in a generic helper:

- query a collection with `query_texts=[query]`
- return the top `n_results`
- extract documents, metadata, distances, and ids
- normalize them into a common source format.

Dedicated retrieval functions then call that helper for each source:

- `retrieve_faq()`
- `retrieve_mandai()`
- `retrieve_uploaded()`
- `retrieve_hybrid()`

The `hybrid` route combines FAQ and Mandai retrieval results, sorts them by distance, and returns the best overall matches.

### Uploaded-file metadata

Uploaded document chunks are stored with metadata such as:

- `file_id`
- `file_name`
- `source_type`
- `chunk_index`

This metadata makes debugging easier and supports future enhancements such as file deletion, filtering, or session-based document isolation.

## Design rationale

Several design choices were made to keep the project suitable for an assignment while still demonstrating agentic behavior:

### 1. Simplicity over full orchestration

The system uses a clean request pipeline instead of a large agent framework. This keeps the code understandable and makes each design choice easier to justify in a report or presentation.

### 2. Explicit routing over hidden retrieval

Different collections are treated as explicit sources rather than silently merged into one search space. This makes the chatbot’s behavior more transparent and aligns well with the assignment requirement to demonstrate routing as an agentic function.

### 3. Grounded answering over creativity

The prompts and retrieval flow prioritize factual grounding over broad conversational flexibility. That is the right trade-off for a documentation and knowledge-base chatbot.

### 4. Practical extensibility

The architecture leaves room for additional features, including:

- uploaded file deletion,
- uploaded file listing,
- image upload and animal description,
- session-level filtering,
- better semantic chunking,
- richer answer citations.

## Limitations and future improvements

The current design is intentionally simple, but several limitations remain:

- The basic fixed-size chunker can split semantically related content.
- Uploaded-file routing depends on explicit references rather than deeper intent modeling.
- The current route classifier artifacts shown in code snapshots require route-label alignment if new routes are added.
- Persistent Chroma state means deleting raw uploaded files alone does not remove indexed embeddings.
- Multi-user isolation is limited unless uploaded documents are also scoped by `session_id`.

Future improvements could include:

- semantic or sentence-aware chunking,
- metadata filtering by session or upload status,
- soft-delete support for uploaded files,
- richer frontend controls for upload management,
- adding image analysis as another agentic tool path.

## Conclusion

This chatbot uses a straightforward but effective RAG architecture: FastAPI handles API orchestration, Streamlit provides the interface, a hybrid router chooses among multiple knowledge sources, Chroma stores vectorized document chunks, and a language model generates grounded answers from retrieved context.

The design is intentionally pragmatic. It demonstrates multiple agentic functions required by the assignment, remains explainable during evaluation, and is extensible enough for future improvements without requiring a major redesign.