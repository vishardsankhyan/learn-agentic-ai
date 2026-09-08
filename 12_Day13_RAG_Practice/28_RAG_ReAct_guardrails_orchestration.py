import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError, Field, BaseModel
from pydantic.networks import IPv4Address
#from typing import Literal

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=20
)

class ValidatedArgs(BaseModel):
    app_name: str
    vip_ip: IPv4Address
    port: int = Field(ge=0, le=65535)
    
    #    app_name: Literal["internal_biling", "public_api"]

CONFLUENCE_DOCS = {
    "internal_billing": "NetScaler VIP Configuration -> IP: 10.50.0.5, Port: 8443",
    "public_api": "NetScaler VIP Configuration -> IP: 172.16.0.10, Port: 443"
}

def search_confluence(app_name: str) -> str:
    normalize_app_name = app_name.lower().replace(" ", "_")

    if normalize_app_name in CONFLUENCE_DOCS:
        return (f"The information for topic {app_name} is result :{CONFLUENCE_DOCS[normalize_app_name]}")
    else:
        return (f"ERROR: The application name was not found on CONFLUENCE DOCS, kindly share correct name")


def deploy_nestscaler_vip(app_name: str, vip_ip: str, port: int) -> str:
    return f"The NetScaler App: {app_name} with VIP {vip_ip} and port: {port} has been deployed"

tool_dispatcher = {
    'search_confluence': search_confluence,
    'deploy_netscaler_vip': deploy_nestscaler_vip
}


search_tool = {
    "type": "function",
    "function": {
        "name": "search_confluence",
        "description": "Searches the confluence doc for the application name",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string"
                }
            },
            "required": ["app_name"]
        }   
    }
}

deploy_tool = {
    "type": "function",
    "function": {
        "name": "deploy_netscaler_vip",
        "description": "This function helps to deploy the Netscaler with App name, VIP_ip and port details",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": { "type": "string"},
                "vip_ip": {"type": "string"},
                "port": {"type": "integer"}
            },
            "required": ["app_name", "vip_ip", "port"]
        }
    }
}


def llm_call(user_input: str):
    """ The Agent check the internal confluence docs and  deploy the NetScaler VIP as per the available information"""

    messages = [
        {"role": "system", "content": "You are a NetScaler Automation Agent. You must NEVER guess VIP IPs or ports. Always use search_confluence to find the exact parameters before calling deploy_netscaler_vip."},
        {"role": "user", "content": user_input}
    ]

    output = []
    current_turn = 0
    max_turn = 4

    while current_turn < max_turn:
        output.append(f"------------- Turn:{current_turn+1}-----------------")
        current_turn += 1

        try:
            response = client.chat.completions.create(
                model="gemini-3.6-flash",
                tools=[search_tool, deploy_tool],
                temperature=0.0,
                messages=messages
            )

            tool_calls = response.choices[0].message.tool_calls
            if not tool_calls:
                output.append(f"The final result: {response.choices[0].message.content}")
                break

            messages.append(response.choices[0].message)
            func_name = tool_calls[0].function.name

            if func_name in tool_dispatcher:
                raw_arg = json.loads(response.choices[0].message.tool_calls[0].function.arguments)

                try:
                    validated_args = ValidatedArgs(**raw_arg)

                    try:
                        if func_name == "search_confluence":
                            result_search = search_confluence(app_name=raw_arg.get("app_name", ""))
                            output.append(f"[CONFLUENCE SEARCH]: {result_search}")
                            messages.append({"role": "tool", "tool_call_id": tool_calls[0].id, "name": func_name, "content": result_search})
                        
                        elif func_name == "deploy_netscaler_vip":
                            result_deploy = deploy_nestscaler_vip(app_name=validated_args.app_name, vip_ip=str(validated_args.vip_ip), port=int(validated_args.port))
                            output.append(f"[DEPLOY STATUS]: {result_deploy}")
                            messages.append({"role": "tool", "tool_call_id": tool_calls[0].id, "name": func_name, "content": result_deploy})

                    except RuntimeError as run_err:
                        output.append(f"RUNTIME ERROR: {run_err}")
                        messages.append({"role": "tool", "tool_call_id": tool_calls[0].id, "name": func_name, "content": str(run_err)})    
                except ValidationError as val_err:
                    output.append(f"VALIDATION ERROR: {val_err}")
                    messages.append({"role": "tool", "tool_call_id": tool_calls[0].id, "name": func_name, "content": str(val_err)})
            else :
                output.append("UNAUTHORIZED FUNCTION CALL")
                messages.append({"role": "tool", "tool_call_id": tool_calls[0].id, "name": func_name, "content": "Unauthorized function request"})
    
        except Exception as e:
            output.append(f"Fatal Error: Observer : {e}")
            messages.append({"role": "tool", "tool_call_id": tool_calls[0].id, "name": func_name, "content": e})
        
    if current_turn >= max_turn:
        output.append("Max turn counter has been hit , so initiatig the circuit breaker ")
    
    return "\n".join(output)

if __name__ == "__main__" :
    user_input = "Please deploy the NetScaler VIP for the internal_billing application."
    print(f"\n\n AGent is running ..\n {llm_call(user_input)}")
                
            
                
                

