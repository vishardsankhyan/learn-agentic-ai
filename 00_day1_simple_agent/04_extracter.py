import os
import json #to convert string to json 
from dotenv import load_dotenv
from openai import OpenAI

#load API key
load_dotenv()

#define client
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

#Defining the function to extract the error code and IP
#def extractor_info(desc: str)-> dict:
def extractor_info(desc: str) -> str:
    """The Agent main function is to extract the ip address and error code from log"""

    #define the system prompt
    #system_prompt = "You are expert log parser in the region, you will return a dictionary containing fieild IP_address which contains IP Address in logs e.g 192.168.12.34 and Error_code e.g Error code 102. "
    system_prompt = "You are expert log parser. You need to filter out IP address and error code from log and retrun a string with ip address and error code seperated by comma e.g. 192.160.23.23,333 . Add no added text or any MD"
    #configuratio the LLM
    response = client.chat.completions.create(
        model="gemini-3.6-flash",
        messages=[
            {"role":"system", "content":system_prompt},
            {"role":"user", "content":desc}
        ]
    )
    raw_text = response.choices[0].message.content #string will be returned here, we need to convert it into diction , so use Json

    #Debug---
    #print(repr(raw_text)) #repr shows us hidden characters e.g "\n" 

    #clean_text = raw_text.replace("```json", "").replace("```", "").strip()
    #return json.loads(raw_text) 
    return raw_text
#defining the main function
if __name__ == "__main__":
    logs = input("Please share the snippet of the logs: ")
    print("Agent is analyzing the logs and will share the results soon....")

    log_agent_info = extractor_info(logs)
    print("Agent result response is: ", log_agent_info)

    #Use standard python to split the string into list by the comma!!
    extracted_data = log_agent_info.split(',')

    if len(extracted_data) == 2:
        ip = extracted_data[0].strip()
        error = extracted_data[1].strip()

        print("Successfull without JSON")
        print(f"-> Extracted IP: {ip}")
        print(f"-> Extrated error: {error}")
    
    else:
        print("Agent did not return exact 2 outptu")

    #print(log_agent_info["IP_address"],"\n",log_agent_info["Error_code"])