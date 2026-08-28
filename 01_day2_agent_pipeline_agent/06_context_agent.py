import os
from dotenv import load_dotenv
from openai import OpenAI

#Load API 
load_dotenv()

#define client
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

#defining the AGent
def answer_client(question: str, run_book: str) -> str :
    """The Agent should provide response from the runbook else not provide the response"""
    #define system prompt
    system_prompt = "You are an expert IT specalist. You will provide the answer to user querry from the run book. incase relevant information is not available in run book response with: escalating the issue to L3"

    #merging the user question and run book in same variable.
    user_message = f"RUNBOOK context: \n{run_book} \n\n USER QUESTION:\n{question}"

    #defining LLM communciation
    response = client.chat.completions.create(
        model="gemini-3.6-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content

#defining the main program

if __name__ == "__main__" :
    
    #Defining the variables
    runbook = "To enable session persistence on the NetScaler or Cloud Load Balancer, navigate to Traffic Management -> Virtual Servers. Select your server, click Edit, and set Persistence Type to SOURCEIP. Timeout defaults to 2 minutes."
    question = "How do I make sure a user's session stays on the same backend server, and what is the default timeout?"

    print("Agent is proessing the question ...")
    agent_response = answer_client(question,runbook)

    print(f"QUESTION: {question}\n\n RUNBOOK: {runbook}\n\n AGENT RESPONSE: {agent_response}")
