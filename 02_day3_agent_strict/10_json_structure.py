import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

JSON_PROMPT = " You are an expert information parser. You extract the name , port and protocol from the user input in natural language. Return a JSON structure reponse with the keys: vs_name, port, proto"


def config_extractor(user_input: str) -> dict:
    """You extract the vservername, port and protocol information from the user input"""

    try:
        response = client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": JSON_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"Error": f"Agent encounterred error {e}"}
    

def config_applier(config: dict) -> str:
    """ This config will apply the configuration"""

    return f"The configuration has been successfully applied: \n vServer Name:{config['vs_name']} \n Port:{config['port']} \n Protocol:{config['proto']}"


#Define the min function
if __name__ == "__main__":
    user_log = input("\n Please share the your input: ")
    print("\nAgent is processing the information ... ")

    agent_response = config_extractor(user_log)

    if "Error" not in agent_response:
        print(config_applier(agent_response))
    else:
        print(f"Error has been encounterred {agent_response['Error']}")
