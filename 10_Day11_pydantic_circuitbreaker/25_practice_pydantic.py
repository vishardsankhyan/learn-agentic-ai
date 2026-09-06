import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import Field, BaseModel, ValidationError
from pydantic.networks import IPv4Address
from typing import Literal

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=20
)

class TarfficRoutingArgs(BaseModel):
    ip_address: IPv4Address
    weight: int = Field(ge=1, le=100)
    environment: Literal["Staging", "Production"]


def route_primary_dc(ip_adrress: str, weight: int, environment: str) -> str:
    raise RuntimeError("Primary DC VLAN allocation exhuasted. Routing failed")


def route_dr_dc(server_ip: str, weight: int, environment: str) -> str:
    return f" Successful {weight}% of {environment} traffic routed to {server_ip} in DR Data Center"

primary_tool = {
    "type": "function",
    "function": {
        "name": "route_primary_dc",
        "description": "This function enabled the routing to the primary server",
        "parameters": {
            "type": "object",
            "properties": {
                "server_ip": { "type": "string"},
                "weight": {"type": "integer"},
                "environment": {"type": "string"}

            },
            "required": ["server_ip", "weight", "environment"]
        }
    }   
}

secondary_tool = {
    "type": "function",
    "function": {
        "name": "route_dr_dc",
        "description": "This function enables the routing to the disaster recovery node with weighted traffic",
        "parameters": {
            "type": "object",
            "properties": {
                "server_ip": {"type": "string"},
                "weight": {"type": "integer"},
                "environment": {"type": "string"}
            },
            "required": ["server_ip", "weight", "environment"]
        }
        
    }
}

tool_dispatcher = {
    'route_primary_dc': route_primary_dc,
    'route_dr_dc': route_dr_dc
}
def llm_call(user_input: str):
    """ The function role to route the traffic to the server from server ip and honoring the weights"""

    messages = [
        {"role": "system", "content": "You are a HA network agent. Always try to route traffic to primary dc first. If primary fails you must fall back to the secondary DC"},
        {"role": "user", "content": user_input}
    ]

    output = []
    current_turn = 0
    max_turn = 5

    while current_turn < max_turn:
        output.append(f"--------Turn count: {current_turn+1}------")
        current_turn += 1

        try:
            response = client.chat.completions.create(
                model="gemini-3.6-flash",
                temperature= 0.0,
                tools=[primary_tool, secondary_tool],
                messages=messages
            )

            tool_calls = response.choices[0].message.tool_calls

            if not tool_calls:
                output.append(f"Final result: {response.choices[0].message.content}")
                break

            messages.append(response.choices[0].message)
            func_name = tool_calls[0].function.name

            if func_name in tool_dispatcher:
                raw_args = json.loads(tool_calls[0].function.arguments)

                try: #Validation
                    validated_args = TarfficRoutingArgs(**raw_args)

                    try:
                        results = tool_dispatcher[func_name](ip_address=str(validated_args.ip_address, weight=int(validated_args.weight), environment=str(validated_args.environment)))
                        output.append(f"The function {func_name} has been successfully run :{results}")
                        messages.append({"role": "tool", "tool_call_id": tool_calls[0].id, "name": func_name, "content": results})
                    
                    except RuntimeError as run:
                        output.append("System Error observed {run}")
                        messages.append({"role": "tool", "tool_call_id": tool_calls[0].id, "name": func_name, "content": str(run)})
                    
                except ValidationError as val_err:
                    output.append("Argument validation error observed")
                    messages.append({"role": "tool", "tool_call_id": tool_calls[0].id, "name": func_name, "content": str(val_err)})
            
            else:
                output.append("LLM has hullucinates and unauthorised tool call")
                messages.append({"role": "tool", "tool_call_id": tool_calls[0].id, "name": func_name, "content": "unauthorised tool"})
        
        except Exception as e:
            output.append(f"Fatal Error :{e}")
            break

    if current_turn  >= max_turn:
        output.append("Max turn has been reached and circuit break")
    
    return "\n".join(output)

if __name__ == "__main__":
    user_input = "Route 150 percent of our production traffic to the new backend server at prod-backend-node."

    print (llm_call(user_input))
            
            
                
                        
                        



