import os
import json 
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def check_iam_policy(email: str, gcp_role: str) -> str:
    return f"Checking the policies for role: {gcp_role} and email: {email} .... Access Granted"

iam_tools = {
    "type": "function",
    "function": {
        "name": "check_iam_policy",
        "description": "The function will return the status of the role and email",
        "parameters": {
            "type": "object",
            "properties": {
                "user_email": {
                    "type": "string",
                    "description": "It is the user email address"
                },
                "user_role": {
                    "type": "string",
                    "description": "It is the user role details"
                }
            },
            "required": ["user_email", "user_role"]
        }
    }
}

#LLM comminucation function
def llm_comm(description: str):
    """"The agent role is to analyze the descriptions and based on email and role share the status of GCP IAM"""

    try:
        response = client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            tools=[iam_tools],
            messages=[
                {"role": "system", "content": "You are an expert GCP IAM policy reviewer. Your job is to check the current status of IAM policies based on user role and email address"},
                {"role": "user", "content": description}
            ]
        )
        tool_calls = response.choices[0].message.tool_calls
        arguments=json.loads(tool_calls[0].function.arguments)

        return check_iam_policy(arguments['user_email'], arguments['user_role'])
    
    except Exception as e:
        return f"Error has been encounterred {e}"


#main function
if __name__ == "__main__":
    user_input = "Please verify if the newly onboarded engineer, alice@example.com, has been assigned the Storage Object Admin permissions."

    print("user input: ",user_input)
    print("Agent is reviewing the information ...")

    agent_response = llm_comm(user_input)
    print(f"\n\nThe Agent response is :\n {agent_response}")