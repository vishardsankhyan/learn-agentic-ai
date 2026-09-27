# Tier 1 Dispatcher & LangGraph State Orchestration

---

## 1. Architectural Concept Mapping (ADC vs. LangGraph)

| ADC / NetScaler Concept | LangGraph Component | Technical Role |
| :--- | :--- | :--- |
| **Virtual Server (VIP)** | `app.invoke()` | Ingress point receiving the user payload and coordinating traffic. |
| **Service Group / Backend Pool** | Nodes (`network_node`, `hardware_node`) | Isolated functional units executing specific logic or tool operations. |
| **Content Switching (CS) Policy** | Conditional Edge (`add_conditional_edges`) | Dynamic routing rule evaluating payload content to direct traffic. |
| **Persistence Profile (Cookie Insert)** | Checkpointer (`SqliteSaver`) + `thread_id` | Database-backed session persistence maintaining conversational context. |
| **Packet Header Rewrite / Normalization** | Reducer (`Annotated[list, add_messages]`) | Appends delta messages to historical state without overwriting prior records. |
| **CLI Script / Running Config** | `builder.compile()` | Validates topology syntax, applies middleware, and locks the graph into an immutable executable. |

---

## 2. Request Lifecycle & State Mutability

```text
[ USER PAYLOAD ]
   │
   │  "user_input" + config={"thread_id": "session_123"}
   ▼
[ 1. INGRESS LOOKUP ] (Moment 1 - Database Read)
   Checkpointer queries SQLite for session history.
   │
   ▼
[ 2. REDUCER MERGE ]
   add_messages appends new message to historical State.
   │
   ▼
[ 3. CONTENT SWITCHING / CONDITIONAL EDGE ]
   Router evaluates payload and decides destination:
   → Returns target node name ("network_pool" or "hardware_pool").
   │
   ▼
[ 4. NODE EXECUTION ]
   Selected backend runs.
   Returns new message payload delta.
   │
   ▼
[ 5. EGRESS COMMIT ] (Moment 2 - Database Write)
   Checkpointer serializes updated state back to SQLite.
   │
   ▼
[ CLIENT RETURN / TERMINATION ]

## 3. Key Takeaways & Debugging Rules

* No Magic Layers: When troubleshooting custom endpoints, explicitly parsing outputs gives you full control over the payload and bypasses hidden vendor bugs.

* Decoupled State Management: Worker nodes never connect directly to databases or track global history; they consume their specific input slice from the State and return only their output delta.

* Deterministic Guardrails: Using exact string matching (typing.Literal) inside Pydantic eliminates conversational hallucinations at the routing layer, ensuring traffic never drops into a black hole.