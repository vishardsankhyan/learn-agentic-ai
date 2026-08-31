import os 
import json 
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def check_bgp(asn: int) -> str:
    return f" The BGP with asn {asn}, has been flapped 4 times in last 60 minutes"

bgp_tool = {
    "type": "function",
    "function": {
        "name": "check_bgp",
        "description": "This function return the BGP flaps status on specific ASN",
        "parameters":{
            "type": "object",
            "properties": {
                "asn": {
                    "type": "integer",
                    "description": "This is the ASN number of a router where BGP is running"
                }
            },
            "required": ["asn"]
        }
    }
}

def llm_call(description: str):
    """The agent is should check the BGP status on the router where ASN is provided in description"""

    try:
        response = client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            tools=[bgp_tool],
            messages=[
                {"role": "system", "content": "You are an L3 network reliability engineer. You provide the status of the network based on the user input"},
                {"role": "user", "content": description}
            ]
        )

        tool_calls = response.choices[0].message.tool_calls
        arguments = json.loads(tool_calls[0].function.arguments)

        return check_bgp(arguments['asn'])
    
    except Exception as e:
        return f"Error has been encountered {e}"
    

#main function
if __name__ == "__main__":
    user_input = "Our NOC is seeing intermittent routing drops. Can you check the stability of autonomous system number 15169?"

    print("\n: user input is :", user_input )
    print("\n\n Agent is processing information ...")

    print("\n\n The response from the LLM agent is : \n", llm_call(user_input))

