import os
from dotenv import load_dotenv
import sqlite3
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.messages import SystemMessage

load_dotenv()

#1. DEFINE THE STATE
# add_messages tells LangGraph to automatically append new messages to the existing list,
# rather than overwriting the list completely.

class State(TypedDict):
    messages: Annotated[list, add_messages]

#2. Initializing the LLM
llm = GoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)

#3 DEFINE THE NODE
def call_node(state: State):
    #the state already contains the conversation history
    response = llm.invoke(state["messages"])
    # We only return the new message to calling function.
    return {"messages": [response]}

#4. BUILD THE GRAPH
builder = StateGraph(State)
builder.add_node("bgyani_agent",call_node)
builder.add_edge(START, "bgyani_agent")
builder.add_edge("bgyani_agent", END)

#5. INITIALIZE THE CHECK POINTER
#We use the local SQLite file so memory survives even if VS CODE is closed
con = sqlite3.connect("bgyani_session.db", check_same_thread=False)
memory = SqliteSaver(con)

#6. COMPILE WITH MEMORY
app = builder.compile(checkpointer=memory)

#7. EXECUTION
if __name__ == "__main__":
    print("[SYSTEM]: BGyani Stateful Agent Booted. Type 'exit' to quit.\n")
    
    # The thread_id is your sticky session ID. 
    # Anyone using "user_session_123" shares the same memory block.
    config = {"configurable":{"thread_id": "user_session_123"}}

    #Inject the system prompt if database is empty
    existing_state = app.get_state(config)
    if not existing_state.values:
        app.update_state(config, {"messages": [SystemMessage(content="You are BGYANI , an IT infrastructre expert")]})

    while True:
        user_input = input("You: ")

        if user_input.lower().strip() == 'exit':
            print("Bye Bye .....")
            break

        # We pass the new input and the config containing the thread_id
        # LangGraph automatically pulls the history from SQLite, runs the LLM, and saves the result
        events = app.invoke({"messages": [("user", user_input)]}, config)

        # Extract the final AI message from the updated state
        print(f"BGYANI: {events['messages'][-1].content}\n")
    