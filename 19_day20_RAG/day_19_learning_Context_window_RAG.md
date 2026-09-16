# BGyaniTech - Agent Development Log
**Focus:** Context Memory Management & RAG Vector Ingestion

## 1. Architectural Milestones
* **Sliding Window Memory:** Implemented instant in-RAM slicing to prevent context overflow. Learned that arrays (`[]`) are strictly required for the `messages` payload because LLM context is a chronological timeline; dictionaries (`{}`) break the schema.
* **Rolling Summary Buffer:** Built a hybrid memory system that uses an LLM to compress older turns into a dense executive summary (preserving IPs, errors, and hostnames) while keeping recent turns raw.
* **Vector Database Ingestion:** Replaced static dictionary runbooks with a local **ChromaDB** instance. Successfully ingested `Document` objects containing NetScaler/infrastructure runbooks and metadata.

## 2. Core Concepts Mastered
* **Cosine Similarity:** Visualized how semantic search relies on the *angle* between vectors rather than their *magnitude* (length). This allows a 3-word user query to perfectly match a 50-page IT runbook if they point toward the same mathematical concept.
* **Model-Agnostic Design:** Utilized LangChain as a universal adapter, demonstrating how to decouple the Embedding Model (Google) from the Chat Model (Groq/Gemini), preventing vendor lock-in.

## 3. Python & Async Gotchas Resolved
* **Async/Await vs Gather:** Realized that `await` explicitly *pauses* the sequential execution of a function until the network request finishes, unlike `asyncio.gather()` which fires tasks in parallel.
* **Tuple Packing/Unpacking:** Learned that returning variables separated by a comma (e.g., `return messages, summary`) automatically creates a tuple, which can be instantly unpacked on the receiving end.
* **Implicit String Concatenation:** Discovered that multi-line strings inside parentheses *without* commas are automatically joined by Python. Adding commas turns them into a tuple, which crashes Pydantic string validation.

## 4. Debugging & Troubleshooting
* **LangChain Restructuring:** Navigated the separation of `langchain-community` and `langchain-chroma` packages.
* **API Endpoint Mismatches:** Handled undocumented 404 errors with Google's embedding model namespace by iterating through endpoint versions until stabilizing on `gemini-embedding-001`.