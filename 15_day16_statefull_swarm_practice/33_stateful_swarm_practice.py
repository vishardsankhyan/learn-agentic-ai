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

route_tool = {
    "type": "function",
    "function": {
        "name": "route_task",
        "description": "Route the requests to specialist agent",
        "parameters": {
            "type": "object",
            "properties": {
                "target_agent": {
                    "type": "string",
                    "enum": ["gyani_g", "it_guy"],
                    "description": "The gyani_g is the reasoning specialist and it_guys is for restarting the server"
                }
            },
            "required": ["target_agent"]
        }
    }
}


swarm_state = {
    "conversation_history":[],
    "target_vip": None,
    "last_agent": "system"
}


def  gyani_g_mock(state: dict) -> dict:
    """ Simulating the triage agent to identify the ip address"""

    # the negative index actually getting the last user conversation 
    latest_user_text = state["conversation_history"][-1]["content"]

    print(f"\n GYANI G WOKE UP ...")
    print(f"\n Gyani G reading the latest user prompt: {latest_user_text}")

    #Write it to the shared memory for other agent's reference.
    print(f"\n GYANI G is writing the '10.20.30.4' to the shared memory")
    state["target_vip"] = "10.20.30.4"

    # Update the conversation history
    state["conversation_history"].append({"role": "assistant", "content": "Diagnosis: the VIP is 10.20.20.4"})

    #Update the last_agent state
    state["last_agent"] = "gyani_g"

    return state


def it_guy_mock(state: dict) -> dict:
    """ Simulating the agent reading the ip address"""

    latest_user_text = state["conversation_history"][-1]["content"]
    print(f" IT GUY WOKE UP ...")
    print(f" The IT GUY is reading the latest user prompt {latest_user_text}")

    #READ from the shared memory
    retreive_vip = state["target_vip"]
    print(f"\n IT GUY got the ip address {retreive_vip} directly from the shared memory")

    state["conversation_history"].append({"role": "assistant", "content": f"Restarted {retreive_vip} server safely"})
    state["last_agent"] = "it_guy"

    return state


def demonstrate_data_isolation(state: dict) -> dict:
    """Proves the use of the extend instead of the append"""
    print("\n\nLLM loading the payload")

    # Create temporary list which store the private system messages
    payload_for_api = [{"role": "system", "content": " You are expert router agent, you reachout to gyani_g for diagnosis and it_guy to perform the actions"}]

    #Adding the context information for the LLM
    payload_for_api.extend(state["conversation_history"])

    print(" printing the payload information received by agent\n")

    for item in payload_for_api:
        print(f"The item is {item}")
    
    print("\n Printing the Conversational history")

    for item in state["conversation_history"]:
        print(f"item {item}")
    
    print(f"JSON output: {json.dumps(state["conversation_history"])}")


#EXECUTION timeline

if __name__ == "__main__":
        #Turn1:User Asks for Diagnosis:
        swarm_state["conversation_history"].append({"role": "user", "content": "Why is the server down"})
        swarm_state = gyani_g_mock(swarm_state)


        #turn2 : Time for execution:
        swarm_state["conversation_history"].append({"role": "user", "content": " go ahead and restart it"})
        swarm_state = it_guy_mock(swarm_state)

        #prove the isolation
        demonstrate_data_isolation(swarm_state)

        print(f"[FINAL OUTPUT]: swam_state is {json.dumps(swarm_state)}")
        print(f"\n\n {swarm_state} ")




