import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

#configuring the LLM 
llm = GoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)

#defining the conversation variable
conversation_variable = [SystemMessage(content="You are BGYANI an helpful IT assistant")]

while True:
    user_input = input("You: ")

    if user_input.lower().strip() == "exit":
        print("Bye Bye ..")
        break

    conversation_variable.append(HumanMessage(content=user_input))
    result = llm.invoke(conversation_variable)

    print(f"BGYANI: {result}\n")
    conversation_variable.append(AIMessage(content=result))
    #print(f"[DEBUG]: result: {result} \n conversation_variable: {conversation_variable}\n")
