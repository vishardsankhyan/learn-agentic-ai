import os
from dotenv import load_dotenv
from openai import OpenAI

#Load the API keys
load_dotenv()

#configure the client
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai"
)

#define function for AI greeter.
def ai_greeter(username: str)->str:
    """ The role of this Agent is to greete the user using username """

    #Defining System Prompt
    system_prompt = "You are an freindly IT helpdesk Assistant. Welcome user by their name and send and ask how you can help them from the nIT team"

    #Configuring the communication with LLM
    response=client.chat.completions.create(
        model="gemini-3.6-flash",
        messages=[
            {"role":"system" , "content": system_prompt},
            {"role":"user" , "content": username}

        ]
    )
    return response.choices[0].message.content

#defining the main program
if __name__=="__main__":
    print("WELCOME TO THE IT DEPT.")
    user_name=input("Please enter you username: ")
    greet_msg=ai_greeter(user_name)
    print("\n",greet_msg)