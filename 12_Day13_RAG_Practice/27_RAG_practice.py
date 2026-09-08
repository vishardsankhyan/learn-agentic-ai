import os 
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=20
)

ERROR_DATABASE = {
    "err_505": "Cause: Network timeout. Fix: Increase gateway timeout to 60s in the config.yaml file.",
    "err_403": "Cause: Permission denied. Fix: Add the user to the 'db-admins' IAM role in Google Cloud Console."
}


def look_error(error_code: str) -> str:
    """It check the ERROR_DATABASE and returns the context information"""
    normalize_error = error_code.lower().replace(" ","_")

    if normalize_error in ERROR_DATABASE:
        return f"[DATABASE RETRIVED]: {ERROR_DATABASE[normalize_error]}"
    
    else:
        return f"[ERROR]: The error not found in database"

error_tool = {
    "type": "function",
    "function": {
        "name": "look_error",
        "description": "The function should check the internal database and return the related content to the error",
        "parameters": {
            "type": "object",
            "properties":{
                "error_code": {
                    "type": "string"
                }
            },
            "required": ["error_code"]
        }
    }
}

tool_dispatcher = {
    'look_error': look_error
}


def llm_call(user_input: str) -> str:
    """The Agent is the database administrator , the Agent should check the internal database ERROR_DATABASE and validate the observation"""

    messages=[
        {"role": "system", "content": "You are an L1 suport agent. You must never guess how to fix an error. Always use look_error tool to find the exact cause and fix from the database"},
        {"role": "user", "content": user_input}
    ]
    output =[]
    current_turn = 0
    max_turn = 4

    while current_turn < max_turn:
        output.append(f"--------- Turn:{current_turn+1}-----------")
        current_turn += 1

        try:
            response = client.chat.completions.create(
                model="gemini-3.6-flash",
                tools=[error_tool],
                temperature=0.0,
                messages=messages
            )

            tool_call = response.choices[0].message.tool_calls

            if not tool_call:
                output.append(f"Final result : {response.choices[0].message.content}")
                break

            messages.append(response.choices[0].message)
            func_name = tool_call[0].function.name

            if func_name in tool_dispatcher:
                raw_arg = json.loads(tool_call[0].function.arguments)
                result = tool_dispatcher[func_name](error_code=raw_arg.get("error_code", ""))

                output.append(f"Reconnaissance: Search for topic: {raw_arg.get('error_code')} and Result: {result}")
                messages.append({"role":"tool", "tool_call_id": tool_call[0].id, "name": func_name, "content": result})
            
            else:
                output.append("Unauthorized tool call: LLM Hilucinated")
                messages.append({"role": "tool", "tool_call_id": tool_call[0].id, "name": func_name, "content": "unauthorized function call"})
        
        except Exception as e:
            output.append(f"Fatal Error: Error has been obseved {e}"),
    
        
        if current_turn > max_turn:
            output.append(f"The max turn values has been reached, so initiating the circuit breaker")
    
    return "\n".join(output)

if __name__ == "__main__":
    user_input = "My database connection just crashed and threw an err_403. How do I fix this?"
    print(f"The result is : \n {llm_call(user_input)}")


    