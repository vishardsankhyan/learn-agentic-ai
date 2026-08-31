import os
import json 
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


def calculate_cdr(ip_address: str, subnet_mask: str) -> str:
    return f"The calcuated CDR for {ip_address}/{subnet_mask} is : 254"

cdr_tool = {
    "type": "function",
    "function": {
        "name": "calculate_cdr",
        "description": "It calcultes the CDR for the ipaddress and subnet provided by user",
        "parameters": {
            "type": "object",
            "properties": {
                "ip_address": {
                    "type": "string",
                    "description": "It is the ip address"
                },
                "subnet_mask": {
                    "type": "string",
                    "description": "It is the subnet mask details"
                }
            },
            "required": ["ip_address", "subnet_mask"]
        }
    }
}


#defining the LLM communication 
def llm_call(user_input: str):
    """The Agent returns the CDR details from IP address and subnet provided by user in natural language"""

    try:
        response = client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            tools=[cdr_tool],
            messages=[
                {"role": "system", "content": "You are expert network engineer. Your job is to return back the CDR details based on IP address and subnet details shared by user"},
                {"role": "user", "content": user_input}
            ]
        )

        tool_calls = response.choices[0].message.tool_calls
        argument = json.loads(tool_calls[0].function.arguments)
        function = tool_calls[0].function.name
    
        print(function)

        #return calculate_cdr(argument['ip_address'], argument['subnet_mask'])
        return function(argument['ip_address', argument['subnet_mask']])
    
    except Exception as e:
        return f"Error has be encountered {e}"

#main function
if __name__ == "__main__":
    user_input = "Can you tell me how many usable hosts I have in the 192.168.1.0 network with a /24 mask?"

    print(f"\n\n User Input: {user_input}")
    print("\n\n Agent is currently accessing the information ....")

    agent_response = llm_call(user_input)

    print(f"\n\n The Agent response: \n {agent_response}")
