# Day 4: Agenti AI
**Topic** Tool Calling & The Agentic Brain

**1. The Tool Calling Architecture**
* **Concept:** LLMs cannot execute code natively. Tool calling is a standardized handoff where the LLM reads a "manual" (JSON schema) of your available Python functions and returns the exact arguments needed to run them.
* **Execution:** Passed the `tools=[health_tool]` argument into the API call. Extracted the AI's generated arguments using `json.loads(response.choices[0].message.tool_calls[0].function.arguments)` and passed them into the local Python function.

**2. JSON Schema Demystified**
* **The Object Container:** In JSON Schema, setting `"type": "object"` at the parameters level dictates that the LLM must return a structured dictionary (key-value pairs) rather than a raw string. 
* **Properties:** The `"properties"` block defines the exact keys and data types (e.g., string, integer) the LLM must generate inside that object.

**3. The Network Execution Flow**
* **Scope & Serialization:** Python locates the global schema dictionary and serializes it into the outgoing HTTP POST request.
* **The Blind LLM:** The model operates entirely in the cloud. It cannot see your local Python functions, logic, or variable scopes. It only reads the text-based JSON payload.
* **The Agentic Decision:** The model compares the user's prompt against the tool's `"description"`. If it finds a match, it halts standard text generation and instead outputs the structured JSON arguments.
* **The Handoff:** Your script receives the JSON string, parses it, and triggers the local execution loop. 
day_04_tool_calling_mechanics.md
Displaying day_04_tool_calling_mechanics.md.