import os
import json
from pydantic import BaseModel, ValidationError
from pydantic.networks import IPv4Address
from dotenv import load_dotenv
from openai import OpenAI

# Define the strict schema 
class RestartVMArgs(BaseModel):
    ip_address: IPv4Address

load_dotenv()

# Client configuration
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def get_ip_address(hostname: str) -> str:
    return f"The ip address for {hostname} is 192.168.23.12"

def restart_vm(ip_address: str) -> str:
    return f"The {ip_address} has been restarted successfully"

ip_tool = {
    "type": "function",
    "function": {
        "name": "get_ip_address",
        "description": "Provides the ip address of the hostname",
        "parameters": {
            "type": "object",
            "properties": {
                "hostname": {
                    "type": "string",
                    "description": "hostname of the machine"
                }
            },
            "required": ["hostname"]
        }
    }
}

vm_tool = {
    "type": "function",
    "function": {
       "name": "restart_vm",
       "description": "This function restarts the VM for provided ip address",
       "parameters": {
          "type": "object",
          "properties": {
             "ip_address": {
                "type": "string",
                "description": "This is machine ip address"
             }
          },
          "required": ["ip_address"]
       }
    }
}

tool_dispatcher = {
   'restart_vm': restart_vm,
   'get_ip_address': get_ip_address
}

def llm_call(user_input: str):
    """It restarts the vm corresponding to the ip address and hostname provided."""
    
    # FIX: Initialize output at the top so the except block can always access it
    output = []
    
    try:
        messages = [
            {"role": "system", "content": "You are the network expert. If a user gives a hostname, convert it to an IP address and restart the VM."},
            {"role": "user", "content": user_input}
        ]

        # Round 1
        response = client.chat.completions.create(
            model="gemini-3.6-flash", # Changed to a valid model version
            temperature=0.0,
            tools=[ip_tool, vm_tool],
            messages=messages
        )

        if not response.choices[0].message.tool_calls:
            return response.choices[0].message.content or "No tools called."
            
        tool_call = response.choices[0].message.tool_calls[0]
        messages.append(response.choices[0].message)
        
        func_name = tool_call.function.name
        
        if func_name in tool_dispatcher:
            arguments = json.loads(tool_call.function.arguments)
            result = tool_dispatcher[func_name](**arguments)
            output.append(f"[Step 1: {func_name} -> {result}]")
            
            messages.append({
               "role": "tool",
               "tool_call_id": tool_call.id,
               "name": func_name,
               "content": result
            })
        else:
            error_msg = f"Error: Unauthorized function call"
            output.append(error_msg)
            messages.append({
               "role": "tool",
               "tool_call_id": tool_call.id,
               "name": func_name,
               "content": error_msg
            })

        # Round 2
        f_response = client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            tools=[ip_tool, vm_tool],
            messages=messages
        )

        f_tool_calls = f_response.choices[0].message.tool_calls

        if not f_tool_calls:
           # If the LLM just replies with text to confirm the restart
           output.append(f"[Final Output] {f_response.choices[0].message.content}")
        else:
            f_tool_call = f_tool_calls[0]
            f_func_name = f_tool_call.function.name

            if f_func_name in tool_dispatcher:
                if f_func_name == "restart_vm":
                    try:
                        raw_args = json.loads(f_tool_call.function.arguments)
                        validated_args = RestartVMArgs(**raw_args)
                        
                        result = restart_vm(ip_address=str(validated_args.ip_address))
                        output.append(f"[Step 2: Successful] {result}")

                    except ValidationError as e:
                       error_msg = f"Validation Error: You provided invalid IP address. Details: {e}"
                       output.append(f"[Guardrail Triggered] {error_msg}")
                else:
                    # Fallback in case it calls another tool
                    raw_args = json.loads(f_tool_call.function.arguments)
                    result = tool_dispatcher[f_func_name](**raw_args)
                    output.append(f"[Step 2: {f_func_name} -> {result}]")
                    
            else:
                output.append(f"[Step 2: Error] Unauthorized tool call: {f_func_name}")
    
    except Exception as e:
      output.append(f"Error observed: {e}")
    
    return "\n".join(output)

if __name__ == "__main__":
   user_input = "Restart the web server at prod-bgyani-frontend."

   print(f"User input: {user_input}\n\nAgent is analyzing...\n\nThe result is:\n{llm_call(user_input)}")