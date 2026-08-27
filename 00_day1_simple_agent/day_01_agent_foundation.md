### Core Agent Architecture ###:
**The Agent Skelton**:
Build pure function with os, dotenv and openai client to execute LLM calls
**System Prompt**:
Used "role": "System" dict to lock LLM into strict single purpose persona

### Python Mechanics and Industry Standard ###
**Type Hint**:
Applied syntax like ***(username: str) -> str:*** explicitly define function input and expected return types for readability.
**Execution Guards**:
Implemented ***if__name__ == "__main__"*** to isolate the test code,ensuring the agent function can be safely imported as tool.
**PEP8 Spacing**:
Mastered the critical distinguish between variable assignment ***(Category == "HARDWARE")*** and removing the space from key argument inside the function ***(model="gemini-3.5-flash)***.
**Listing Indexing and Cleaning**:
Used [0], [1] to access any particular item in array and .split() to sanetise and remove the invisible whitespaces.

### Agentic Pattern Built ###
**Single purpose Agent**:
Designed a foundational agent to ingest to ingest raw text and output a strictly formatted translation.
**The Router**:
Forced LLM to retrun specific string ("NETWORK","HARDWARE","SOFTWARE") to seamlessly trigger downstream python.
**The Guardrail**:
used LLM to validate input topic and return a boolean True/False
**Robust Extraction**:
Bypassed common JSON Markdown trap by prompting LLM for simple comma seperated strings, using python built in function .split().