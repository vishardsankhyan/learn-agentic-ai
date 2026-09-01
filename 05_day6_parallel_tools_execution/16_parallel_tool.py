import os 
import json
from dotenv import load_dotenv
from openai import OpenAI

#loading keys
load_dotenv()

#print(f"Key loaded successfully: {bool(os.getenv('GROQ_API_KEY'))}")

#defining the client configuration
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

#Groq API keys

#client = OpenAI(
#    api_key=os.getenv("GROQ_API_KEY"),
#    base_url="https://api.groq.com/openai/v1"
#)


#defining the function for cpu status
def get_cpu_status(server_name: str) -> str:
    """Returns the CPU metrics"""

    return f"The Cpu metrics for server {server_name} is 60%"


#defining function to return the bgp flap status
def get_bgp_flap(asn: int) -> str:
    """Returng the BGP flap fap status for provided asn number"""

    return f"The router is with asn {asn} has been flapped 5 times in last 60 minutes"

#Tools schema for get_cpu_status

cpu_tool = {
    "type": "function",
    "function": {
        "name": "get_cpu_status",
        "description": "This function returns the status of the CPU",
        "parameters": {
            "type": "object",
            "properties": {
                "server_name": {
                    "type": "string",
                    "description": "This is server name"
                }
            },
            "required": ["server_name"]
        }
    }
}

bgp_tool = {
    "type": "function",
    "function": {
        "name": "get_bgp_flap",
        "description": "This function returns the bgp flaps observed on router",
        "parameters": {
            "type": "object",
            "properties": {
                "asn": {
                    "type": "integer",
                    "description": "This is the router asn number"
                }
            },
            "required": ["asn"]
        }
    }
}

tool_dispatcher = {
    'get_cpu_status': get_cpu_status,
    'get_bgp_flap': get_bgp_flap
} 
#deining the LLM communication 
def llm_call(user_input: str):
    """This agent returns the CPU metrics and BGP flap status for provided server"""

    try:
        response = client.chat.completions.create(
            model="gemini-3.6-flash",
            #model="openai/gpt-oss-120b",
            temperature=0.0,
            tools=[cpu_tool, bgp_tool],
            messages=[
                {"role": "system", "content": "You are expert network engineer and provide the server technical and metric details as requested by user"},
                {"role": "user", "content": user_input}
            ]
        )

        tool_calls = response.choices[0].message.tool_calls
        func_output = ""
        for tool in tool_calls:
            function_name = tool.function.name
            arguments = json.loads(tool.function.arguments)
        
            func_output += f"\n {tool_dispatcher[function_name](**arguments)}"
            
        return func_output
    
    except Exception as e:
        return f"There is an Error obseserved {e}"

#defininig the main fucntion.
if __name__ == "__main__":
    user_input = "Production is lagging. Check the CPU load on prod-web-01 and verify the BGP route stability for ASN 15169."

    print("Agent is analyzing: ....")

    agent_response = llm_call(user_input)
    print("\n\n Agent response is :\n", agent_response)