import os
from dotenv import load_dotenv
from openai import OpenAI

#Load API key
load_dotenv()

#Defien client
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai"
)

#defining the Agent function

def is_it_topic(description: str) -> bool:
    """The Role of this Agent is to return a boolean if description matches the categories"""
    # Defining the System prompt
    system_prompt = "You are a strict IT ticket reviewer. Please make sure the ticket category belongs to Cloud Computing, Networkig or IT infrastructure. Return True if it matches the category else return False"

    #Confiuring the LLM 
    response = client.chat.completions.create(
        model="gemini-3.5-flash",
        messages=[
            {"role":"system", "content": system_prompt},
            {"role":"user", "content": description}
        ]
    )
    result = response.choices[0].message.content
    if result.strip() == "True": 
        return True
    else:
        return False

if __name__ == "__main__":
    description = input("Share your concern here: ")
    print("\nAgent is classifying the category of your")
    if is_it_topic(description):
          print("Your resquest is being forwarded to the concerned team")
    else:
         print("Blocked:Please share your concern related to Cloud computing, Networking or IT infrastructure")