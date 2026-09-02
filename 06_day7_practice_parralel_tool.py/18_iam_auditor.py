import os
import json
from dotenv import load_dotenv
from openai import OpenAI

#Loading the API Keys
load_dotenv()

#Defining the client configuration
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

#defining function to chck permission
def check_user_permission(email: str) -> str:
    return f"The {email} has the permission."

#defining function to check the access keys
def list_service_access_keys(sa_name: str) -> str:
    return f"The {sa_name} has 2 access keys associated with the account"

#LLM Schema for tools
permission_tool = {
    "type": "function",
    "function": {
        "name": "check_user_permission",
        "description": "This function provides the iam permission status for any user associated with email",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "This is the email address"
                }
            },
            "required": ["email"]
        }
    }
}

access_tool = {
    "type": "function",
    "function": {
        "name": "list_service_access_keys",
        "description": "It provides the status of the access keys associted with the sa name",
        "parameters": {
            "type": "object",
            "properties": {
                "sa_name": {
                    "type": "string",
                    "description": "This is the user sa name"
                }
            },
            "required": ["sa_name"]

        }
    }        
}

tool_dispatcher = {
    'check_user_permission': check_user_permission,
    'list_service_access_keys': list_service_access_keys
}

def llm_call(user_input: str):
    """ The Agent job is to share the IAM permissions and access keys details"""

    response = client.chat.completions.create(
        model="gemini-3.6-flash",
        temperature=0.0,
        tools=[permission_tool, access_tool],
        messages=[
            {"role": "system", "content": "You are expert Google cloud system admin and help user with the related queries"},
            {"role": "user", "content": user_input}
        ]
    )

    tool_calls = response.choices[0].message.tool_calls

    output = [] # defining the list/array to contain the output generated

    if not tool_calls:
        return f"{response.choices[0].message.content}" or "There is some error occurrred"
    else:
        for tool in tool_calls:
            func_name = tool.function.name
            arguments = json.loads(tool.function.arguments)

            if func_name in tool_dispatcher:
                func = tool_dispatcher[func_name]
                output.append(func(**arguments))
            
            else:
                output.append("error has been encountered")
    
        return "\n".join(output)

if __name__ == "__main__":
    user_input = "Audit the security posture. Check the permissions for admin@bgyani.co.in and list the keys for the 'deployer-bot' service account."

    print ("\n\n User Input: ",user_input)
    print("\n\n Agent is processing ....")

    print (f"\n\n Agent response: {llm_call(user_input)}")