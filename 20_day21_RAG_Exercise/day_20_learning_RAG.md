# BGyaniTech - Agent Development Log
**Date:** September 18, 2026
**Focus:** RAG Document Loaders, Chunking, and Quota Management

## 1. Document Loaders (The Input Layer)
* **WebBaseLoader:** Uses `beautifulsoup4` under the hood to scrape live URLs, strip HTML tags, and extract raw text into a single LangChain `Document` object. Automatically captures the source URL in the metadata.
* **PyPDFLoader:** Reads local PDF files using `pypdf`. It is highly efficient because it automatically splits the document page-by-page and injects the exact `page` number into the metadata, which is critical for citing sources in the BGyani triage agent.

## 2. Text Splitting & The Sliding Window
* **RecursiveCharacterTextSplitter:** Essential for breaking massive strings into digestible mathematical vectors. 
* **Chunk Overlap:** Configured a `chunk_overlap` (e.g., 200 characters). This creates a sliding window that ensures a critical technical sentence isn't severed in half exactly at the chunk boundary, preserving semantic meaning for the embedding model.

## 3. Managing Cloud API Quotas
* **The 429 Error:** Learned that feeding an entire web page's worth of chunks into `Chroma.from_documents()` instantly trips the Gemini free-tier rate limits (Requests/Tokens Per Minute).
* **The Slice Hack:** Used standard Python list slicing (`chunked_docs[:5]`) to send only the first 5 chunks to the database. This allows for rapid testing of the RAG mechanics without getting temporarily banned by the API.

## 4. Local vs. Cloud Embeddings
* **Cloud (Google/Gemini):** Fast and powerful, but subject to API limits, network latency, and naming changes (e.g., the `gemini-embedding-001` endpoint shift).
* **Local (HuggingFace):** Explored `HuggingFaceEmbeddings` (specifically `all-MiniLM-L6-v2`). Proved that a local, 80MB model can run safely on a laptop's CPU, providing infinite, free embeddings while guaranteeing zero data leakage of internal IP addresses or infrastructure logs.

## 5. Python & LangChain Gotchas
* **Modular Ecosystem:** Experienced how LangChain recently broke its monolithic library into smaller packages (`langchain-community`, `langchain-text-splitters`, `langchain-chroma`). Each must be `pip installed` explicitly.
* **Syntax Precision:** A single missing letter (`lanchain` vs `langchain`) throws a `ModuleNotFoundError`.