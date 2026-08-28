import os
from dotenv import load_dotenv
from openai import OpenAI

#Load API 
load_dotenv()

#Client confguration 
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),  
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

SLA_PROMPT = " You are expert escalation analyzer. Review the customer email and categorize it with the priority (P1: The complete outage, P2: For partial outage, P3: minor bug). Return string with Priority and impacted services with comma seperated, e.g. P1, NetScaler GSLB service"

#defining the Agent function
def escalation_analyzer(cust_email: str) -> str:
    """The Agent has job to review the customer email and return the priority of the case and impacted services"""

    try:
        #LLM coommunication
        response = client.chat.completions.create(
            model="gemini-3.6-flash",
            temperature=0.0,
            messages=[
                {"role": "system", "content": SLA_PROMPT},
                {"role": "user", "content": cust_email}
            ]
        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"ERROR, API Failure: {e}"
    

#Main function
if __name__ == "__main__":
    Test_Email = "Our main production database cluster is completely down and no customers can log in to the e-commerce portal. We are losing money by the minute."

    agent_response = escalation_analyzer(Test_Email)

    if "ERROR" not in agent_response:
        list_response = agent_response.split(',')
        print(f"\n\nThe priority of the case: {list_response[0].strip()} \n")
        print(f"The component impacted: {list_response[1].strip()}")
    else:
        print(agentt_response)