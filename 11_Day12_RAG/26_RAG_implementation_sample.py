import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=20
)

#Enterprise KnowledgeBase:
RUNBOOK = {
    "database_migration": "To migrate the customer DB, use port 5432 and set the max_connections flag to 1000.",
    "firewall_policy": "All internal traffic must be routed through VLAN 40 with strict TLS 1.3 enforcement."
}

def search_runbook(topic: str) -> str:
    """ Searches engineering runbook for the configuration parameters"""
    normalized_topic = topic.lower().replace(" ", "_")

    if normalized_topic in RUNBOOK:
        return f"[DOC Reterived] : {RUNBOOK[normalized_topic]}"

    else:
        return f"[ERROR] Topic {topic} not found in runbook. Try some other search"

search_tool = {
    "type": "function",
    "function": {
        "name": "search_runbook",
        "description": "The function will search the topic in the RUNBOOK and return the status",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string" 
                }
            },
            "required": ["topic"]
        }
    }
}

tool_dispatcher = {
    'search_runbook': search_runbook
}

def runbook_agent(user_input: str):
    """An Agent should retreives context from answering"""
    messages=[
        {"role": "system", "content": "You are expert Cloud architect. You donot assume the parameters or configurations. You should search the topic in the search_runbook to verify the details in the RUNBOOK before answering"},
        {"role": "user", "content": user_input}
    ]

    output = []
    current_turn = 0
    max_turn = 4

    while current_turn < max_turn:
        output.append(f"---------Turn: {current_turn+1}-----------------")
        current_turn += 1

        try:
            response = client.chat.completions.create(
                model="gemini-3.6-flash",
                temperature=0.0,
                tools=[search_tool],
                messages=messages
            )

            tool_calls = response.choices[0].message.tool_calls

            if not tool_calls:
                output.append(f"Final result : {response.choices[0].message.content}")
                break
            
            #Tool execution
            messages.append(response.choices[0].message)
            func_name = response.choices[0].message.tool_calls[0].function.name

            if func_name in tool_dispatcher:
                raw_args = json.loads(tool_calls[0].function.arguments)
                results = tool_dispatcher[func_name](topic=raw_args.get("topic", ""))

                output.append(f"[Reconnaissance]: search for '{raw_args.get('topics')}'. Result: {results}")

                #feed teh retrived document back to LLM
                messages.append({"role":"tool", "tool_call_id": tool_calls[0].id, "name": func_name, "content": results})
            else:
                output.append("LLM Hullicnated and unauthorised tool call")
                messages.append({"role":"tool", "tool_call_id": tool_calls[0].id , "name": func_name, "content": "unauthorized tool"})

        except Exception as e:
            output.append(f"The error observed {e}")
            break

        if current_turn > max_turn:
            output.append(f" Max turn reached and circuit breaker tripped")
        
    return "\n".join(output)
    
if __name__ == "__main__":
    user_input = "What are the exact settings required to perform a database migration?"
    print(runbook_agent(user_input))



