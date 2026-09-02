import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def resolve_dns(hostname: str) -> str:
    return f"The IP address for {hostname} is 192.168.1.32"

def ping_ip(ip_address: str) -> str:
    return f"Ping is successful to {ip_address} and latency is 15ms"

resolve_tool = {
    "type": "function",
    "function": {
        "name": "resolve_dns",
        "description": "Function to convert hostname to ip address",
        "parameters": {
            "type": "object",
            "properties": {
                "hostname" : {
                    "type": "string",
                    "description" : "hostname of a network device"
                }
            },
            "required": ["hostname"]
        }
    }
}

ping_tool = {
    "type": "function",
    "function": {
        "name": "ping_ip",
        "description": "Performs the ping to an ip address",
        "parameters": {
            "type": "object",
            "properties": {
                "ip_address": {
                    "type": "string",
                    "description": "It is the ip address of a networking device"
                }
            },
            "required" : ["ip_address"]
        }
    }
}

tool_dispatcher = {
    'resolve_dns': resolve_dns,
    'ping_ip': ping_ip

}

def llm_call(user_input: str) -> str:
    """Provides the Netork connectivty statistics"""

    try:
        messages = [
            {"role": "system", "content": "You are expert network admin"},
            {"role": "user", "content": user_input}
        ]
        response = client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            tools=[resolve_tool, ping_tool],
            messages=messages
        )

        tool_calls = response.choices[0].message.tool_calls[0]

        messages.append(response.choices[0].message) #adding the LLM decision as context

        output = []

        func_name = tool_calls.function.name

        if func_name in tool_dispatcher:
            arguments = json.loads(tool_calls.function.arguments)
            result =  tool_dispatcher[func_name](**arguments)
            output.append(f"[Step1: {func_name}] {result}")

            #Append actual tool output to the context hostory
            messages.append({
                "role": "tool",
                "tool_call_id": tool_calls.id,
                "name": func_name,
                "content": result
            })

            #Second API call
            final_response = client.chat.completions.create(
                model="gemini-3.6-flash",
                temperature=0.0,
                tools=[resolve_tool, ping_tool],
                messages=messages
            ) 

            final_tool_calls = final_response.choices[0].message.tool_calls[0] 

            if not final_tool_calls:
                return final_response.choices[0].message.content or "Error: in second agent"

            else:
                ffunc = final_tool_calls.function.name
                farguments = json.loads(final_tool_calls.function.arguments)

                if ffunc in tool_dispatcher:
                    fresult = tool_dispatcher[ffunc](**farguments)
                    output.append(f"[Step2: {ffunc}]: {fresult}")
                else:
                    output.append("Error: Unauthorized 2nd step call")
                
                return "\n".join(output)
            
    except Exception as e:
        return f"Error has been encountered : {e}"

                          

if __name__ == "__main__":
    user_input = "I cannot reach the database. Resolve the IP for db.bgyani.co.in and then ping it to check latency"

    print(f"\n\nUser Input: {user_input}")
    print(f"\n\n Agent is thinking ... \n\n Response: {llm_call(user_input)} ")
