import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

#client configuration
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def get_instance_id(hostname: str) -> str:
    return f"The {hostname} has the instance id as i_0abcd123456efghj5678"

def fetch_error_log(instance_id: str) -> str:
    return f"Critical error has been encountered for {instance_id}, There are memory crash event ecountered"

instance_tool = {
    "type": "function",
    "function": {
        "name": "get_instance_id",
        "description": "Provides the instances id for any hostname",
        "parameters": {
            "type": "object",
            "properties": {
                "hostname": {
                    "type": "string",
                    "description": "It is the hostname"
                }
            },
            "required": ["hostname"]
        }
    }
}

error_tool = {
    "type": "function",
    "function": {
        "name": "fetch_error_log",
        "description": "It captures the logs related to the instance id provided",
        "parameters": {
            "type": "object",
            "properties": {
                "instance_id": {
                    "type": "string",
                    "description": "It is the instance id for the instance"
                }
            },
            "required": ["instance_id"]
        }

    }
}

tool_dispatcher = {
    'get_instance_id': get_instance_id,
    'fetch_error_log': fetch_error_log
}
#function llm call

def llm_call(user_input: str) -> str:
    """ It is provding the instance id for hostname and later checks the related errors as well"""

    try:
        messages = [
            {"role": "system", "content": "You are expert cloud incident responder and help with the error logs details"},
            {"role": "user", "content": user_input}
        ]

        response = client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            tools=[instance_tool, error_tool],
            messages=messages
        )

        tool_calls = response.choices[0].message.tool_calls[0]

        output = []
        messages.append(response.choices[0].message) #Adding history to context

        func_name = tool_calls.function.name

        if func_name in tool_dispatcher:
            arguments = json.loads(tool_calls.function.arguments)
            result = tool_dispatcher[func_name](**arguments)
            output.append(f"[step 1: {func_name} : result {result}]")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_calls.id,
                "name": func_name,
                "content": result
                })
    
        else:
            error_msg = f"Error: illegal function call {func_name}"
            output.append(error_msg)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_calls.id,
                "name": func_name,
                "content": error_msg
            })
        #2nd iteration

        f_response = client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            tools=[instance_tool, error_tool],
            messages=messages

        )

        f_tool_call = f_response.choices[0].message.tool_calls
        

        if not f_tool_call:
            return f_response.choices[0].message.content or "Investigation complete"
        
        else:
            f_tool_calls = f_tool_call[0]
            f_func_name = f_tool_calls.function.name
            if f_func_name in tool_dispatcher:
                f_arguments = json.loads(f_tool_calls.function.arguments)
                f_result = tool_dispatcher[f_func_name](**f_arguments)
                output.append(f"[Step2: {f_func_name}, {result}]")
            
            else:
                output.append(f"Step2: Illegeal function call {f_func_name}")
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Error has been encounteres {e}"


if __name__ == "__main__":
    user_input = "The web server 'prod-web-front' just crashed. Find its instance ID and then pull its error logs."

    print("user input:", user_input)

    print("\n\n Agent is thinking ... \n\n Agent response: \n",llm_call(user_input))

