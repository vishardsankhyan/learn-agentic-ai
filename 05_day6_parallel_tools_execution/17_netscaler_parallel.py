import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

print(f"Whether key is loaded properly: {bool(os.getenv("GEMINI_API_KEY"))}")

#configuring the client
#client = OpenAI(
#    api_key=os.getenv("GEMINI_API_KEY"),
#    base_url="https://generativelanguage.gogoleapis.com/v1beta/openai"
#)

#Configuring Groq
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1/"
)


def check_vip_status(vip_address: str) -> str:
    return f"The is VIP {vip_address} is up and runing fine"


def get_backend_latency(pol_name: str) -> str:
    return f"The backend pool {pol_name}, is experiencing high latency"

#LLM schema
vip_tool = {
    "type": "function",
    "function": {
        "name": "check_vip_status",
        "description": "This function returns the VIp status on NetScaler",
        "parameters": {
            "type": "object",
            "properties": {
                "vip_address": {
                    "type": "string",
                    "description": "This represents the VIP address of NetScaler"
                }
            },
            "required": ["vip_address"]
        }
    }

}
latency_tool = {
    "type": "function",
    "function": {
        "name": "get_backend_latency",
        "description": "This function provides the latency of backend services",
        "parameters": {
            "type": "object",
            "properties": {
                "pol_name": {
                    "type": "string",
                    "description": "It is the backedn services pol name"
                }
            },
            "required": ["pol_name"]
        }
    }
}

tool_dispatcher = {
    'check_vip_status': check_vip_status,
    'get_backend_latency': get_backend_latency
}

#defining the LLM
def llm_call(user_input: str):
    """ The Agent should with the Netscaler specific requirements from user"""

    try:
        response = client.chat.completions.create(
            #model="gemini-3.6-flash",
            model="openai/gpt-oss-120b",
            temperature=0.0,
            tools=[vip_tool, latency_tool],
            messages=[
                {"role": "system", "content": "You are expert netscaler l3 engineer and expertise on NetScaler device"},
                {"role": "user", "content": user_input}
            ]
        )

        tool_calls = response.choices[0].message.tool_calls

        #if None in tool_calls: <-- can cause program crash if LLM returns no list
        if not tool_calls #safe option checks if None or no list
            return (f"{response.choices[0].message.content}") or " There are some issue observed"
        
        else:
            output =[]
            for tool in tool_calls:
                function_name = tool.function.name
                arguments = json.loads(tool.function.arguments)

                if function_name in tool_dispatcher: #guardrails to address LLM hillucination : LLM some random function
                    func = tool_dispatcher[function_name]
                    func_output = func(**arguments)
                    output.append(func_output)
                else:
                    output.append(f" Unknown errors has been observed {function_name}")
            
            return "\n".join(output)
            
    except Exception as e:
        return f"Error has been encountered {e}"

if __name__ == "__main__":
    user_input = "The main checkout portal is slow. Check the status of VIP 192.168.100.5 and get the latency for the 'checkout-backend-pool'."
    
    print(f"user_input: {user_input}")
    print("\n\n Agent is thinking ....")
    
    agent_response = llm_call(user_input)
    
    print("\n Agent response: \n", agent_response)
    
