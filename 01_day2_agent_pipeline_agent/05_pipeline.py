import os
from dotenv import load_dotenv
from openai import OpenAI

#load the API keys
load_dotenv()

#define client config
client = OpenAI(
    api_key = os.getenv("GEMINI_API_KEY"),
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
)

#Defining the translator Agent
def it_translator(french_summary: str) -> str:
    """The job role of this Agent is to translate the French ticket summary to English"""

    #Define system prompt for translator.
    system_prompt = "You are an expert IT translator. Translate the user Text in French into English. Return only english translation text and add no additional conversational fillers"

    #Configuring the communciation with LLM
    response = client.chat.completions.create(
        model = "gemini-3.6-flash",
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": french_summary}
        ]
    )

    return response.choices[0].message.content

#Defining the IT summarizer Agent
def it_summarizer(eng_summary: str) -> str:
    """Agent role is to summarize the english summary of the ticket"""

    #define system prompt to summarize IT simmary
    system_prompt = "You are an expert L3 IT engineer. Review the IT ticket details and provide a summary of the incident for easy understandablity"

    #Defining the LLM communication
    response = client.chat.completions.create(
        model = "gemini-3.6-flash",
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": eng_summary}
        ]
    )
    return response.choices[0].message.content

#defining the main function

if __name__ == "__main__" : 
    incident_report = "Le serveur web principal (web-node-01) est en panne depuis 03h00 du matin. La base de données ne répond pas aux requêtes de lecture et les clients perdent la connexion TCP. Nous devons redémarrer le cluster immédiatement avant la corruption des données."

    print("Incident is: ",incident_report)
    print("\n Invoking the Translator Agent ....")
    eng_sum = it_translator(incident_report)

    print("Step1: English summary of the incidence: \n",eng_sum)

    print("\n Invoking the IT summrizer event ...")
    it_sum = it_summarizer(eng_sum)

    print("setp2: IT summarizer output.. \n", it_sum)