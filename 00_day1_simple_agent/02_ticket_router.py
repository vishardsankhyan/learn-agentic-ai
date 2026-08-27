import os
from dotenv import load_dotenv
from openai import OpenAI

#Load the API files
load_dotenv()

#define Client
client = OpenAI(
    api_key = os.getenv("GEMINI_API_KEY"),
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
)

#define the agent function router
def ticket_router(ticket: str) -> str:
    """ The Agent task is to categorize the ticket in 3 categories HARDWARE, SOFTWARE, NETWORK"""

    #defining the system_prompt
    system_prompt = "You are a strict IT ticket classifier. You review the ticket description and return one of the 3 matching category . The categories are HARDWARE, SOFTWARE, NETWORK. Agent should return strictly matching category and  no other content or text"

    #defining LLM communication 
    response = client.chat.completions.create(
         model = "gemini-3.6-flash",
         messages = [
             {"role":"system", "content": system_prompt},
             {"role":"user", "content": ticket}
         ]
    )
    return response.choices[0].message.content

#defining the main function

if __name__ == "__main__":
    ticket_desc = input("Please enter your ticket details: ")
    print("Agent is categorizing the ticket ....")
    category = ticket_router(ticket_desc)

    
    print("\n Agent response:", category)

    if category == "HARDWARE": print("Sending pager message to hardware team ...")
    elif category == "SOFTWARE": print("sending pager message to software team ...")
    elif category == "NETWORK": print("sending pager message to network team ...")
    else : print("Mannual Review is required Now....")