import os
from dotenv import load_dotenv
from openai import OpenAI

#load the API Key
load_dotenv()

# Define the Client 
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai"
)

#Define the Agent
def polite_translator(messay_thought: str)-> str:
    """" The role of this Agent is simple to retrun a polite version of the statements."""
    #Define system prompt
    system_prompt="You are an expert industry communication assistant. Your job is to return a polished, professional and polite version of the user's input"

    #Configure the LLM interaction
    response=client.chat.completions.create(
        model="gemini-3.6-flash",
        messages=[
            {"role":"system" , "content": system_prompt},
            {"role":"user" , "content": messay_thought}
        ]
    )
    #print (response.choices[0].message.content)

    return response.choices[0].message.content

if __name__ == "__main__":
    user_input="This is a complete messy situation and I want someone to take the responsibility and take our boat to the seashore  else everthing will be doomed"

    print("user input is :", user_input)
    print("Waiting for the response from the LLM ......")

    polite_ver=polite_translator(user_input)

    print("response from the LLM:\n",polite_ver)
