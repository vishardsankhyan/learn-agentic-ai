import os
import json
from dotenv import load_dotenv
from openai import OpenAI

#Loading the environemnt variable
load_dotenv()

#defining the client 
client = OpenAI(
    api_key = os.getenv("GEMINI_API_KEY"),
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
)


#defining the get health status function.
def get_vip_status(vip: str) -> str:
    return f"The NetScaler VIP {vip} is marked UP and running healthy"


#defining the tools for LLM understanding.
vip_tools = {
    "type": "function",
    "function": {
        "name": "get_vip_status",
        "description": "The function returns the current health status of the NetScaler VIP, VIP name is provided as argument",
        "parameters": {
            "type": "object",
            "properties": {
                "vip_name": {
                    "type": "string",
                    "description": "It is the name of the netsclaer VIP e.g. lb_vip"
                }
            },
            "required": ["vip_name"]
        }
    }
}


#Communication with LLM
def llm_comm(description: str):
    #Agent should review the description and provide the response or tool name in return as per the description.

    try:
        response = client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            tools=[vip_tools],
            messages=[
                {"role": "system", "content": "You are expert netscaler engineer. You review the description of the issue and suggest the next action to share the health of the VIP or anyother entity"},
                {"role": "user", "content": description}
            ]
        )

        #print(response)
        content = response.choices[0].message.content
        print("\ncontent:", content)
        tool_calls = response.choices[0].message.tool_calls
        print("\ntool_calls: ",tool_calls)

        arguments = json.loads(tool_calls[0].function.arguments)

        return get_vip_status(arguments['vip_name'])

    except Exception as e:
        return f"\nError has been encounterred {e}"

#defining main function
if __name__ == "__main__":
    user_input = "Please check if the main prod-web-vip is currently active."

    print ("\n\nUser Input: ", user_input)
    print("\n\n Agent is processing information ...")

    agent_response = llm_comm(user_input)

    print("\n\n The Agent response is ... \n\n", agent_response)