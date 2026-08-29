# Day 2: Pipelines, Context Grounding, & Enterprise Architecture

## 1. Prompt Chaining (The Two-Step Pipeline)
* **Concept:** Complex AI tasks shouldn't be handled by one massive prompt. We broke tasks into modular functions and chained them together.
* **Execution:** Passed the returned output of `it_translator()` directly into the input of `it_summarizer()`. This modularity is the foundation of complex agentic workflows.

## 2. Context-Grounded Agents (Introduction to RAG)
* **Concept:** Prevented AI hallucinations by forcing the LLM to answer using *only* a specific document (like an IT Runbook). 
* **Execution:** Solved the "Missing Context Bug" by using Python **f-strings** to merge the system's context and the user's question into a single `user_message` before sending it to the API: 
  `user_message = f"RUNBOOK:\n{runbook}\n\nQUESTION:\n{question}"`

## 3. Enterprise Architectural Standards
* **Separation of Concerns (Constants):** Moved system prompts out of the functions and into global constants (e.g., `SLA_PROMPT`) at the top of the file. This separates AI business logic from Python execution logic.
* **Deterministic Outputs (Temperature):** Added `temperature=0.0` to the OpenAI client call to strip away AI creativity, forcing it to provide robotic, highly consistent outputs required for IT infrastructure tasks.
* **Fault Tolerance (Try/Except):** Wrapped the API network calls in a `try/except` block *inside* the function. This ensures that if the OpenAI API goes down, the function returns a graceful error string instead of crashing the entire master application.

## 4. Advanced PEP 8 Formatting
* **Vertical Spacing:** Learned the "Two Blank Lines" rule (always put two blank lines before and after a top-level function) and the "One Blank Line" rule (used inside functions to separate logical chunks).
* **Naming Conventions:** Reinforced that standard variables should be completely lowercase (`test_email`), while global constants are completely uppercase (`SLA_PROMPT`).