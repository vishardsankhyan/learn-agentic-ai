# LangGraph Multi-Agent Architecture: Engineering Concepts

## 1. State & Routing Policy (The Payload & ACLs)
* **`State(TypedDict)`**: The global packet blueprint. The `Annotated[list, add_messages]` reducer ensures that when a node returns new data, it is safely appended to the chat history array rather than overwriting it.
* **`RoutingTicket(BaseModel)`**: The Content Switching (CS) Policy. By using `Literal["network_pool", "hardware_pool"]`, we create a mathematical strict-whitelist. The LLM cannot invent new routing destinations; it must pick a valid backend pool.

## 2. The VIP Dispatcher Pipeline (LCEL)
The routing engine uses **LangChain Expression Language (LCEL)** to process the packet through a 3-step assembly line: `router_chain = router_prompt | llm | parser`.
* **`PydanticOutputParser`**: Reads the `RoutingTicket` class and translates its rules into hidden JSON instructions for the LLM. It also intercepts the LLM's raw text output and decodes it back into a Python Object.
* **`PromptTemplate`**:
  * `partial_variables`: Pre-prints the hidden JSON formatting rules into the prompt when the script boots (saves processing overhead).
  * `input_variables`: Injects the user's actual live message at runtime.

## 3. Backend Specialist Agents (SystemMessage Injection)
Instead of hardcoding separate AI models, we use a single locked-in firmware (`gemini-3.6-flash`) and dynamically change its "Operating System" per node.
* **Payload Assembly**: `llm.invoke([sys_msg] + state["messages"])`
* By gluing a hidden `SystemMessage` (e.g., "You are a Tier 3 Network Engineer") to the front of the user's chat history array, we force the LLM into a specific persona right before execution. This system prompt is never saved to the database or shown to the user.
* **Output Normalization**: Nodes must return `{"messages": [response]}` to satisfy the State's reducer rules.

## 4. Content Switching Logic (Dynamic Edges)
* **Message Isolation**: `user_payload = state["messages"][-1].content` grabs only the most recent user text, stripping away LangChain metadata.
* **Object Decoding**: After the pipeline executes, the `decision` variable is a validated Pydantic object, not a dictionary. We use dot notation (`decision.destination`) to extract the exact pool name and hand it to LangGraph for routing.

## 5. Topology & Persistence Binding (The Control Plane)
* **Storage Socket**: `conn = sqlite3.connect("bgyani_sessions.db", check_same_thread=False)` opens a persistent, dedicated read/write socket to a local file, acting like a Fibre Channel connection to a SAN. `SqliteSaver` translates LangGraph data into raw SQL.
* **Committing the Config**: `app = builder.compile(checkpointer=memory)` validates the network topology, locks it from further changes, and permanently binds the storage driver. The resulting `app` object is the fully executable software.