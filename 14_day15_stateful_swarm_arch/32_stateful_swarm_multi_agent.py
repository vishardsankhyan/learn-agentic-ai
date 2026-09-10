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

#Virtual Tool

route_tool = {
    "type": "function",
    "function": {
        "name": "route_task",
        "description": "Route the task to correct agent specilist",
        "parameters": {
            "type": "object",
            "properties": {
                "target_agent": {
                    "type": "string",
                    "enum": ["gyani_g", "it_guy"],
                    "description": "The gyani_g is the diagnosis/search specilist. The it_guy is for restarting the services"
                }
            },
            "required": ["target_agent"]
        }
    }
}

def gyani_g_triage(state: dict) -> dict:
    print("\n The traffic is routed to the gyani g \n")
    print(f"\n\n init state: {state}")
    user_prompt = state["conversation_history"][-1]["content"]

    #Simulating the datavase query
    found_ip = "10.50.0.5"

    #Write to shared memory
    state["target_vip"] = found_ip
    state["last_agent"] = "gyani_g"

    #Appending the response to the conversation history
    response_msg = f" Diagnosis complete. The payment gateway bound to ip {found_ip} needs to restart"
    state["conversation_history"].append({"role": "assistant", "content": response_msg})
    print(f"[GYANI G OUTPUT]: {response_msg}")

    print(f"\n\n return state: {state}")
    return state


def it_guy_execution(state: dict) -> dict:
    print("\n IT Guy performing the restart activity \n")
    print(f"\n\n init state: {state}")

    #Read from the shared memory
    target_vip = state["target_vip"]
    state["last_agent"] = "it_guy"

    if not target_vip:
        error_msg = f"I cannot execute. GYANI G has not provided the target vip in the shared state yet"
        state["conversation_history"].append({"role": "assistant", "content": error_msg})
        print(f"[IT GUY OUTPUT]: {error_msg}")
        print(f"\n\n Return state: {state}")
        return state
    
    print(f"The IT GUY has found the {target_vip} in shared memory and will proceed for the restart activity")

    #simulate the execution
    message = f"The taget machine with ip {target_vip} has been started successfully"
    state["conversation_history"].append({"role": "assistant", "content": message})
    print(f"[IT GUY OUTPUT]: {message}")

    print(f"\n\n Return state: {state}")
    return state

#Supervisor Function

def bgyani_supervisor(state: dict) -> dict:
    print("[BGYANI SUPERVISOR] Analyzing the content .....")

    #passing the conversational history to the agent for full content
    message_for_llm = [{"role": "system", "content": " You are BGYANI SUPERVISOR, route diagnostic quert to gyani_g and route action/restart queries to it_guy"}]
    message_for_llm.extend(state["conversation_history"])

    response = client.chat.completions.create(
        model="gemini-3.6-flash",
        tools=[route_tool],
        tool_choice={"type": "function", "function":{"name": "route_task"}},
        temperature=0.0,
        messages=message_for_llm
    )

    tool_calls = response.choices[0].message.tool_calls

    if tool_calls:
        try:
            raw_arg = json.loads(tool_calls[0].function.arguments)
            target = raw_arg.get("target_agent")
            print(f"[SUPERVISOR]: target: {target}")

            if target == "gyani_g":
                return gyani_g_triage(state)
            
            elif target == "it_guy":
                return it_guy_execution(state)
            
            else:
                print("[ERROR]: The supervisor has hallucinated and sent the unknown agent")
        
        except json.JSONDecodeError:
            print("[ERROR]: Json parsing failed")
    
    return state

#main continuous loop

if __name__ == "__main__":
    #initialize swarm state
    swarm_state = {
        "conversation_history": [],
        "target_vip": None,
        "last_agent": "system"
    }

    #Turn1 Diagnostic 
    print("========== TURN 1 ==========")
    prompt_1 = "Why is the payment gateway throwing an ERR_503?"
    print(f"User: {prompt_1}")

    swarm_state["conversation_history"].append({"role":"user", "content": prompt_1})
    swarm_state = bgyani_supervisor(swarm_state)


    #Turn2:  Execution request
    print("\n========== TURN 2 ==========")
    prompt_2 = "Great, go ahead and restart it."
    print(f"User: {prompt_2}")

    swarm_state["conversation_history"].append({"role": "user", "content": prompt_2})
    swarm_state = bgyani_supervisor(swarm_state)

    print(f"\n[FINAL OUTPUT]: {json.dumps(swarm_state, indent=2)}")


