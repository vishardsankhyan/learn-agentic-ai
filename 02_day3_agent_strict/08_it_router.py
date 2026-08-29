import os
from dotenv import load_dotenv
from openai import OpenAI

#Load the API keys
load_dotenv()

#define client
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
   )
#Define the Router prompt
ROUTER_PROMPT = " You are an export IT Router. You categorize the problem or ticket in one of the three categories (HARDWARE,SOFTWARE,CLOUD). Incase you are not certain about the category then set category as UNKNOWN. You only return the identified Category only"


#definng the Routing function
def it_routing(ticket_summ: str) -> str:
    """The Agent shoudl return the one of the category for the event categories are HARDWARE, SOFTRWARE, CLOUD and UNKNOWN incase none of previous category fits"""
    try:
        response = client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            messages=[
                {"role": "system", "content": ROUTER_PROMPT},
                {"role": "user", "content": ticket_summ}
            ]
        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error observed :{e}"


#Defining the main function
if __name__ == "__main__":
    ticket = input("\nPlease enter the issue: ")
    print("\nAgent processing your request ...")
    agent_response = it_routing(ticket)

    if "Error" not in agent_response:
        if "UNKNOWN" not in agent_response:
            print(f"The issue is categorized as {agent_response} and sent to the concerned team")
        else:
            print("Unfortnately: Issue was not ategorized by Agent and team will get back to you soon")
    else:
        print(f"An error has been observed during processing and Agent get back to you. Error details \n{agent_response}")    