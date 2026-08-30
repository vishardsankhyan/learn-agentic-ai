import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def get_server_status(server: str) -> str:
    """This function retruns the dummay output"""

    return f"Server {server} is online and RUNNING at 45%"

#Tool Schema:"Instruction manual" for LLM to read and understand pythin code
health_tool = {
    "type": "function",
    "function": {
        "name": "get_server_status",
        "description": "Check the current health and CPU status of a specific server.",
        "parameters": {
            "type": "object",
            "properties": {
                "server_name": {
                    "type": "string",
                    "description": "The name of the server. eg web-01, prod-01"
                }
            },
            "required": ["server_name"]
        }
    }
}

def route_request(usr_input: str):
    try:
        response=client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            tools=[health_tool],
            messages=[
                {"role": "system", "content": "you are expert in analzing the health check and report and share the health report"},
                {"role": "user", "content": usr_input}
            ]
        )
        tool_calls = response.choices[0].message.tool_calls
        argument = json.loads(tool_calls[0].function.arguments)
        result = get_server_status(argument["server_name"])

        return result
    except Exception as e:
        return f"Error has been encounterred {e}"

if __name__ == "__main__":
    user_input = "Can you check if our frontend node web-01 is healthy?"

    print("Agent reviewing the information ...\n\n")

    res = route_request(user_input)

    print(f"User input:   {user_input}\n\n Agent response: \n{res}")
