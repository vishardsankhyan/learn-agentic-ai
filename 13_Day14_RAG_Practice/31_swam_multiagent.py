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

def gyani_g_triage(user_input: str) -> str:
    """Gyan G isolated the ReAct loop. Ony has read tools"""
    print("[ROUTED TO]: Gyani G Triage specialist")
    messages = [
        {"role":"system", "content": "You are Gyani G, a triage expert. Diagnose the issue using monitoring and runbook tools."},
        {"role": "user", "content": user_input}
    ]

    return "Gyani G diagnosis complete.."

def it_guy_execution(user_input: str) -> str:
    """Teh IT Guys isolate the ReAct loop. Only has the write tools"""
    print("[ROUTED TO]: IT Guy Triage speciliaist")

    messages = [
        {"role": "system", "content": "You are The IT Guy. You safely execute runbook commands with strict parameter validation."},
        {"role": "user", "content": user_input}
    ]

    return "IT execution is completed .."

#supervisor has only one tool access 

route_tool = {
    "type": "function",
    "function": {
        "name": "route_task",
        "description": "Routes the task to correct agent specilist",
        "parameters" : {
            "type": "object",
            "properties": {
                "target_agent": {
                    "type": "string",
                    "enum" : ["gyani_g", "it_guy"],
                    "description": "The gyani_g for seach and diagnostics anf it_guy for the execution"
                }
            },
            "required": ["target_agent"]
        }
    }
}


def bgyani_supervisor(user_input: str):
    """BGyani analyzes intent and hands off the prompt."""
    print("[BGYANI SUPERVISOR]: Analyzing the user request ....")

    response = client.chat.completions.create(
        model="gemini-3.6-flash",
        tools=[route_tool],
        tool_choice={"type": "function", "function": {"name": "route_task"}},
        temperature=0.0,
        messages=[
            {"role": "system", "content": "You are BGyani, the supervisor. Route diagnostic questions to gyani_g. Route action/restart requests to it_guy."},
            {"role": "user", "content": user_input}
        ]
    )

    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        raw_args = json.loads(tool_calls[0].function.arguments)
        target = raw_args.get("target_agent")

        #The Handoff
        if target == "gyani_g":
            return gyani_g_triage(user_input)
        
        elif target == "it_guy":
            return it_guy_execution(user_input)
        
        else:
            return("The Supervisor Hallucinated as unknown agent")
        
    return "[ERROR]: Supervisor failed to route the task."


if __name__ == "__main__":
# Scenario A: Diagnosis (Will route to Gyani G)
    prompt_1 = "Why is the payment gateway throwing an ERR_503?"
    
    # Scenario B: Execution (Will route to The IT Guy)
    prompt_2 = "Restart prod-vip-01 in the prod environment."
    
    print("--- Scenario A ---")
    print(bgyani_supervisor(prompt_1))
    
    print("\n--- Scenario B ---")
    print(bgyani_supervisor(prompt_2))
