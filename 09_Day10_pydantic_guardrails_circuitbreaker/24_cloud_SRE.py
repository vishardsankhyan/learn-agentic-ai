import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError
from typing import Literal

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout =20
)

# Pydantic GuardRails
class RouterConfigArgs(BaseModel):
    region: Literal["us_east","eu_west","ap_south"]
    delay: int = Field(ge=0, le=60)


#Target system outages (The tools)
def restart_primary_router(region: str, delay: int) -> str:
    """Simulate the hard reboot of the primary"""
    raise connectionError(f"HTTP 503: The server in {region} is unresponsive.")

def restart_backup_router(region: str, delay:int) -> str:
    """Simulate the backup router is working normal and fallback up mechanism"""
    return f"The backup node on {region} has been started with {delays} in seconds"

#Tool schema

primary_tool = {
    "type": "function",
    "function": {
        "name": "restart_primary_router",
        "description": "It restarts the primary router",
        "parameters": {
            "type": "object",
            "properties": {
                "region": {
                    "type": "string",
                    "description": "It is the region of the cloud asset"
                },
                "delay":{
                    "type": "integer",
                    "description": "It is the delay for restart"
                }
            },
            "required": ["region", "delay"]
        }
    }
}

secondary_tool = {
    "type": "function",
    "function": {
        "name": "restart_backup_router",
        "description": "It restarts the backup router once the primary router is failed",
        "parameters": {
            "type":"object",
            "properties": {"region":{"type": "string"}, "delay":{"type": "integer"}},
            "required":["region", "delay"]

        }
    }
}

tool_dispatcher = {
    'restart_primary_router': restart_backup_router,
    'restart_backup_router': restart_backup_router
}

def resilient_agent(user_input: str):
    """It validates the argument, infinit loop and resilient to exceptions"""

    output = []
    messages = [
        {"role": "system", "content": "You are an expert SRE and amke sure you restart the instance in mentioned region in case of failure use backup instance to restart with mentioned delays"},
        {"role": "user", "content": user_input}
    ]

    #Circuit breaker
    turn_count = 0
    max_count = 4 # Hard limit on the API call avoid infinite calls

    while turn_count < max_count:
        output.append(f"\n-----Turn{turn_count+1}------")
        turn_count += 1

        try:
            response = client.chat.completions.create(
                model="gemini-3.6-flash",
                temperature=0.0,
                tools=[primary_tool, secondary_tool],
                messages=messages
            )

            #1. Exit condition
            if not response.choices[0].message.tool_calls:
                output.append(f"Final result: {response.choices[0].message.content}")
                break #Exit the while loop

            tool_calls = response.choices[0].message.tool_calls[0]
            messages.append(response.choices[0].message)
            func_name = tool_calls.function.name

            if func_name in tool_dispatcher:
                #Execution of pydantic guardrails
                raw_args = json.loads(tool_calls.function.arguments)

                #Catch target system outage
                try:
                    validated_arg = RouterConfigArgs(**raw_args)
                    
                    try:
                        result = tool_calls[func_name](region=validated_arg.region, delay=int(validated_arg.delay))

                        output.append(f"[Tool Success] {func_name} is executed successfully")
                        messages.append({"role":"tool", "tool_call_id": tool_calls.id, "name": func_name, "content": result})

                    except ConnectionError as api_err:
                        output.append("[System Outage detected {api_err}]")
                        messages.append({"role": "tool", "tool_call_id": tool_calls.id, "name": func_name, "content": str(api_err)})
                
                except ValidationError as val_err:
                    output.append("[Pydantic Guardrail] LLM huccination wromg arguments]")
                    messages.append({"role": "tool", "tool_call_id": tool_calls.id, "name": func_name, "content": f"Validation Error: {val_err}"})
            
            else:
                messages.append({"role":"tool", "tool_call_id": tool_calls.id, "name": func_name, "content": "Unauthorized Tool" })

        except Exception as e:
            output.append(f"[Fatal Error] : {e}")
            break
    
    if turn_count >= max_count:
        output.append("Max trun has been reached circuit breaker")
    
    return "\n".join(output)


if __name__ == "__main__":
    user_input = "Restart the primary router in us-north immediately with a 10 second delay."
    print(resilient_agent(user_input))


        