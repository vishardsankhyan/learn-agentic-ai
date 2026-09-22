# BGyaniTech - Agent Development Log
**Focus:** LCEL Pipelines and Interpreting API Warnings

## 1. LangChain Expression Language (LCEL)
* **The Pipe Operator (`|`):** LCEL mimics the Linux pipe. It forces a strict, one-way data flow where the output of one component automatically becomes the input of the next (`chain = prompt | llm | parser`).
* **Why it matters:** While agents use dynamic `while` loops for reasoning, the underlying steps they take are built on these rigid, predictable LCEL chains.

## 2. LCEL Component Breakdown
* **ChatPromptTemplate:** Acts as the formatter. It ingests a raw Python dictionary (`{"concept": "BGP"}`) and translates it into a standardized `PromptValue` containing system and human message roles.
* **The LLM (ChatGoogleGenerativeAI):** The processor. It takes the `PromptValue` and returns a complex `AIMessage` object containing the text, token counts, and safety metadata.
* **StrOutputParser:** The clean-up crew. It intercepts the `AIMessage` and strips away all metadata, passing down only the raw, print-ready Python string.

## 3. Interpreting SDK Warnings
* **Actionable Warnings (Fixed Sampling):** Requesting a non-existent model version (like `gemini-3.6-flash`) causes the API to fall back to hardcoded defaults, completely ignoring parameters like `temperature=0.0`. 
* **Upstream Warnings (AFC):** Warnings about "Automatic Function Calling (AFC)" or deprecated endpoints are often directed at the library maintainers (LangChain), not the end-user. If the library hasn't updated to Google's newest endpoint, the warning prints locally but does not break the agent's logic.