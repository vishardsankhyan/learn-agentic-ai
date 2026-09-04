import os
import json
from pydantic import BaseModel, ValidationError, Field
from typing import Literal
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class SecurityRuleArg(BaseModel):
    port: int = Field(ge=1 , le=65535)
    protocol: Literal["TCP", "UDP"]

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def add_security_rule(port: int, protocol: str) -> str:
    return f"Successfully opened port {port} for {protocol} traffic."

security_tool = {
    "type": "function",
    "function": {
        "name": "add_security_rule",
        "description": "It opens the firewall port for any protocol",
        "parameters": {
            "type": "object",
            "properties": {
                "port": {"type": "integer", "description": "It is the port number"},
                "protocol": {"type": "string", "description": "It is the protocol details"}
            },
            "required": ["port", "protocol"]
        }
    }
}

tool_dispatcher = {
    "add_security_rule": add_security_rule
}

def llm_call(user_input: str):
    """Firewall security expert that opens ports and protocols."""
    
    output = [] # Moved to top for safety

    try:
        messages = [
            {"role": "system", "content": "You are a Cloud Security Agent. Users will ask you to open firewall ports. You must use the add_security_rule tool. Do not ask for clarification."},
            {"role": "user", "content": user_input}
        ]

        # ROUND 1
        response = client.chat.completions.create(
            model="gemini-3.6-flash", # Fixed model name
            temperature=0.0,
            tools=[security_tool], # Removed quotes
            messages=messages
        )

        if not response.choices[0].message.tool_calls:
            return "Error: No tool was called."

        tool_call = response.choices[0].message.tool_calls[0]
        messages.append(response.choices[0].message)
        func = tool_call.function.name

        if func == "add_security_rule":
            try:
                raw_arg = json.loads(tool_call.function.arguments)
                validated_arg = SecurityRuleArg(**raw_arg)
                result = add_security_rule(port=validated_arg.port, protocol=validated_arg.protocol)
                output.append(f"[Successful Round 1: {result}]")
                
            except ValidationError as e:
                # ROUND 1 FAILED - ENTERING RETRY CIRCUIT
                errormsg = f"Validation Error: {e}. You must use TCP or UDP."
                output.append(f"[Round 1 Failed] Guardrail caught bad protocol.")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func,
                    "content": errormsg
                })
                
                # ROUND 2 (Inside the except block)
                new_response = client.chat.completions.create(
                    model="gemini-3.6-flash",
                    temperature=0.0,
                    tools=[security_tool],
                    messages=messages
                )
                
                if not new_response.choices[0].message.tool_calls:
                    output.append("[Round 2 Failed] Agent gave up.")
                    return "\n".join(output)

                new_tool_call = new_response.choices[0].message.tool_calls[0]
                messages.append(new_response.choices[0].message) # Append assistant message
                
                new_func = new_tool_call.function.name
                
                if new_func == "add_security_rule":
                    # Fix: Parse JSON and validate again in Round 2
                    new_raw_arg = json.loads(new_tool_call.function.arguments)
                    try:
                        new_validated = SecurityRuleArg(**new_raw_arg)
                        result = add_security_rule(port=new_validated.port, protocol=new_validated.protocol)
                        output.append(f"[Round 2 Recovery Successful] {result}")
                    except ValidationError as new_e:
                        output.append(f"[Round 2 Failed Again] {new_e}")
                
        else:
            output.append(f"Error: Invalid function call")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"System Exception occurred: {e}"

if __name__ == "__main__":
    user_input = "Please open the standard web port for HTTP traffic. Do not ask me for clarification, just guess."
    print(f"User Input: {user_input}\n\nAgent is processing...\n\nResult:\n{llm_call(user_input)}")