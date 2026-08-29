import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

JSON_PROMPT = "You are expert logs parser. Extract the hostname, OS and IP address from the provided log. Return the output in JSON format and strictly keys: hostname, OS, IP"

def log_parser(log: str) -> dict:
    """ AGent should process log and provide Hostname, OS, IP"""
    try:
        response = client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": JSON_PROMPT},
                {"role": "user", "content": log}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        #return f"Error is observed :{e}"  --> It is sending string not Dict and would cause a bug in main line #37
        return {"Error": f"Agent failure: {e}"}


if __name__ == "__main__":
    user_input = input("Please enter the log: ")
    print("\n Agent is processing the logs...")
    agent_response = log_parser(user_input)

    if "Error" not in agent_response:
        print("Agent has proceessed the information, please refer below for summary\n")
        #print(agent_response)
        print(f"Hostname: {agent_response['hostname']}\n")
        print(f"OS: {agent_response['OS']}\n")
        print(f"IP: {agent_response['IP']}")
    else:
        print(f"Error has been encountered while Agent processing{agent_response}")



    
