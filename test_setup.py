import os
from dotenv import load_dotenv
from openai import OpenAI

#Load API Key from .env
load_dotenv()

# Configure the Client to point to Google's Gemini endpoint
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta" 

)

print("Sending send request to Gemini .... ")

response = client.chat.completions.create(
    model="gemini-3.6-flash",
    messages=[
        {"role": "system", "content": "You are helpful AI assistant"},
        {"role": "user", "content":"Say 'playground setup is completed' in a voice of freindly robot"}
    ]
)

print(f"\nResponse:\n{response.choices[0].message.content}")