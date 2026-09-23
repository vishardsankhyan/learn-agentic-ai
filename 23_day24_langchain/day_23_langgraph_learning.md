# BGyaniTech - Agent Development Log
**Date:** September 23, 2026
**Focus:** LangGraph Routing Logic and Data Payload Debugging

## 1. LangGraph as a Content Switching vServer
* **The Architecture:** A LangGraph router node functions exactly like a Tier 1 dispatcher or a NetScaler Content Switching policy. It does not solve the ticket; it analyzes the intent and forwards the `State` payload to a specialized backend node (e.g., Hardware, Software, Network).
* **Conditional Edges:** The routing table of the graph. The graph pauses execution, evaluates the output of the router node, and dynamically maps the traffic to the next function.

## 2. Debugging Payload Structures (The `AttributeError`)
* **The Error:** `AttributeError: 'str' object has no attribute 'content'`
* **The Cause:** When expecting a complex API response packet (an `AIMessage` object containing metadata and headers), asking for `.content` extracts the text. If an OutputParser or specific model variation intercepts the response and strips the metadata first, the code receives a raw Python string. Strings do not have a `.content` attribute.
* **The Fix:** Treat the response as raw text immediately (`category = response.strip().lower()`). 
* **The Takeaway:** Always verify whether a node is receiving the full packet (object) or just the raw payload (string) before attempting to parse it.