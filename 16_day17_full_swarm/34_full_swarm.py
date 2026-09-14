import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from typing import Literal

#Setting Up the configuration

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=20
)

#Configure the LLM Model.
LLM_MODEL = "gemini-3.6-flash"

#Databases and validation
MONITORING_ALERTS = {
    "payment_gateway": "CRITICAL: VServer down. Code: ERR_503",
    "inventory_api": "WARN: High latency. Code: ERR_TIMEOUT"
}

RUNBOOK = {
    "ERR_503": "VServer backend overload. Action required: restart_vserver. Target: prod-vip-01, Env: prod",
    "ERR_TIMEOUT": "Database locked. Action required: clear_cache. Target: db-cluster-main, Env: prod"
}

class ValidationArgs(BaseModel):
    target_vip: str
    env: Literal["prod", "staging"]

#3.Python execution function
def check_monitoring(app_name: str) -> str:
    normalize_input = app_name.lower().replace(" ","_")
    if normalize_input in MONITORING_ALERTS:
        return f"[Result]: {app_name} {MONITORING_ALERTS[normalize_input]}"
    
    return f" [ERROR]: Alert no found"


def search_runbook(err_code: str) -> str:
    normalize_err = err_code.upper().replace(" ", "_")
    if normalize_err in RUNBOOK:
        return f"[RESULT]: {err_code} : {RUNBOOK[normalize_err]}"
    return f"[ERROR]: {err_code} not found in RUNBOOK"


def restart_server(target_vip: str, env: str) -> str:
    return f"The {target_vip} restarted in the {env} environment"


tool_dispatecher = {
    'check_monitoring': check_monitoring,
    'search_runbook': search_runbook,
    'restart_server': restart_server
}

# JSON Tool schema

route_tool = {
    "type": "function",
    "function": {
        "name": "route_task",
        "description": "It routes the request to the specialist agent",
        "parameters": {
            "type": "object",
            "properties": {
                "target_agent": {
                    "type": "string",
                    "enum": ["gyani_g", "it_guy"],
                    "description": "The gyani_g performs the diagnosis and it_guy performs the actions"
                }

            },
            "required": ["target_agent"]
        }
    }
}

monitor_tool = {
    "type": "function",
    "function": {
        "name": "check_monitoring",
        "description": "the tool check the application in the alert database and retruns the error code in return",
        "parameters": {
            "type": "object",
            "properties": { "app_name": {"type": "string"}},
            "required": ["app_name"]
        }
    }
}

search_tool = {
    "type": "function",
    "function": {
        "name": "search_runbook",
        "description": "Search the database for the error and returns the action to be performed",
        "parameters": {
            "type": "object",
            "properties": {"err_code": {"type": "string"}},
            "required": ["err_code"]
        }
    }
}

restart_tool = {
    "type": "function",
    "function": {
        "name": "restart_server",
        "description": "It restarts the targeted VIP server",
        "parameters": {
            "type": "object",
            "properties": {
                "target_vip": { "type": "string"},
                "env": {"type": "string"}
            },
            "required": ["target_vip", "env"]
        }
    }
}

#Specilist worker
def gyani_g_triage(state: dict) -> dict:
    print("[GYANI GONLINE]: Initiating the online triage")

    #private and public history
    message_for_llm = [
        {"role": "system", "content": "You are L2 expert and use the check_monitoring and search_runbook to understand the issue and find the target vip ip. Summarize your findings clearly"}
    ]

    message_for_llm.extend(state["conversation_history"])

    current_turn = 0
    max_turn = 5

    while current_turn < max_turn:
        current_turn += 1

        response = client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            tools=[monitor_tool, search_tool],
            messages=message_for_llm
        )

        message = response.choices[0].message
        message_for_llm.append(message)

        if not message.tool_calls:
            print(f"[GYANI G FINAL DIAGNOSIS]: {message.content}")
            # write only the final answer to public memory
            state["conversation_history"].append({"role": "assistant", "content": message.content})
            state["last_agent"] = "gyani_g"
            break

        #tool execution
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            try:
                raw_arg = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as json_err:
                message_for_llm.append({"role": "assistant", "content": str(json_err)})
                continue

            if func_name == "check_monitoring":
                m_result = tool_dispatecher[func_name](app_name=raw_arg.get("app_name", ""))
                message_for_llm.append({"role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": m_result})
                print(f" The GYANI G checked monitoring : {m_result}")
            
            elif func_name == "search_runbook":
                s_result = tool_dispatecher[func_name](err_code=raw_arg.get("err_code",""))
                message_for_llm.append({"role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": s_result})
                print(f"GYANI G searched runbook {s_result}")
                
    return state

def it_guy(state: dict) -> dict:
    print(f"[THE IT GUY IS ONLINE]: Preparation for execution")

    message_for_llm = [
        {"role": "system", "concern": "You are IT Expert. Read the conversation history and get teh target VIP and environment details and use restart_vser tool to execute the actions"}
        ]
    
    message_for_llm.extend(state["conversation_history"])

    current_count = 0
    max_count = 5

    while current_count < max_count:
        current_count += 1

        response = client.chat.completions.create(
            model=LLM_MODEL,
            temperature=0.0,
            tools=[restart_tool],
            messages=message_for_llm
        )

        message = response.choices[0].message
        message_for_llm.append(message)

        if not message.tool_calls:
            print(f"[IT GUYS]: Final message {message}")
            state["conversation_history"].append({"role":"assistant", "conversation": message})
            state["last_agent"] = "it_guy"
            break

        #Tool Execution with HILT and pydantic
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name

            if func_name == "restart_server":
                raw_arg = json.loads(tool_call.function.arguments)
                try:
                    validatedarg = ValidationArgs(**raw_arg)
                except ValidationError as v_err:
                    message_for_llm["conversation_history"].append({"role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": v_err})
                    print(f"[IT GUY]: Validation Error : {v_err}")
                    continue

                #HILT 
                print("\n AUTHORIZATION IS REQUIRED \n")
                print(f"Target VIP: {validatedarg.target_vip}, Environment: {validatedarg.env}")
                approval = input("Please share your consent in y/n").strip().lower()

                if approval == 'y':
                    try:
                        r_result = tool_dispatecher[func_name](target_vip=str(validatedarg.target_vip), env=str(validatedarg.env))
                        message_for_llm["conversation_history"].append({"role": "tool", "tool_call_id": tool_call.id ,"name": func_name, "content": r_result})
                        print(f"[IT GUY]: executed {r_result}")
                    
                    except RuntimeError as run_err:
                        message_for_llm["conversation_history"].append({"role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": str(run_err)})                                                                                                                             
                        print(f"[IT GUY]: Run time error {str(run_err)}")
                    
                else: 
                    message_for_llm.append({"role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": "AUTHORIZATION FAILED: user did not give concent to move forward"})
                    print("[IT GUY]: User authorization failed")

    return state

#Supervisor 
def bgyani_supervisor(state: dict) -> dict:
    print("\n [BGYANI_ SUPERVISOR AGENT]: Initializing the agent ...")

    message_for_llm = [
        {"role": "system", "content": "You are an expert route. You review the conversation history and route gyani_g for the diagnosis and it_guy for restarting server or performing the actions"}
    ]
    message_for_llm.extend(state["conversation_history"])

    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.0,
        tools=[route_tool],
        tool_choice={"type": "function", "function":{"name": "route_task"}},
        messages=message_for_llm
    )

    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        try:
            raw_arg = json.loads(tool_calls[0].function.arguments)
            target=raw_arg.get("target_agent")

            if target == "gyani_g":
                return gyani_g_triage(state)
            elif target =="it_guy":
                return it_guy(state)
            else:
                print("[ERROR]: Supervisor Hallucinated...")
        except json.JSONDecodeError:
            print("[SUPERVISOR ERROR]: JSON Parsor failure")
    
    return state


# Main continous Loop
if __name__ == "__main__":
    #Initialize the blank shared state
    swarm_state = {
        "conversation_history":[],
        #"target_vip": None, : removing it from hardcoded to make it more flexible
        "last_agent": "system"
    }


# Turn 1: Triage Request
print("============Turn1:============")
prompt_1 = "Why the payment gateway is down ?"
print(f"User {prompt_1}")
swarm_state["conversation_history"].append({"role": "user", "content": prompt_1})

swarm_state = bgyani_supervisor(swarm_state)

#Turn2: Execution 
print("============Turn2===========")
prompt_2 = "Great go ahead and execute the plan"
print(f"User: {prompt_2}")
swarm_state["conversation_history"].append({"role": "user", "content": prompt_2})

swarm_state = bgyani_supervisor(swarm_state)

print("=========== FINAL OUTPUT ================")
print(json.dumps(swarm_state["conversation_history"], indent=2))


    








