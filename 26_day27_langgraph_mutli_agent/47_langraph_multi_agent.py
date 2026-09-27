import os
import warnings
import sqlite3
from dotenv import load_dotenv
from typing import Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.checkpoint.sqlite import SqliteSaver

warnings.filterwarnings("ignore", message=".*direct use of AFC in Models.generate_content_stream utomatic function calling*.")
warnings.filterwarnings("ignore", message=".* uses fixed sampling defaults*.")
warnings.filterwarnings("ignore", message=".*we recommend to use AFC in Chat.send_message*.")

load_dotenv()

#1. STATE and ROUTING 
class State(TypedDict):
    messages: Annotated[list, add_messages]

class RoutingTicket(BaseModel):
    destination: Literal["network_pool", "hardware_pool"] = Field(description="Route the user IT issue to the correct backend node pool")

#2. ENGINE and PIPELINES
llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)

#Tier 1 VIP dispatcher pipline
parser = PydanticOutputParser(pydantic_object=RoutingTicket)
router_prompt = PromptTemplate(
    template="You are a strict IT routng dispacther.Read the user issue and route it .\n{formal_instructions}\n User Issue:{issue}",
    input_variables=['issue'],
    partial_variables={"formal_instructions": parser.get_format_instructions()}
)
router_chain = router_prompt | llm | parser

#3. BACKEND SERVER
def network_node(state: State):
    print("[BACKEND]: Network Engine processing packet ...")
    #We inject specific System Prompt for backedn node
    sys_msg = SystemMessage(content="You are a Tier 3 Network Engine. You troubleshoot routing, BGP, Load Balancing, and DNS. Respond technically but concisely.")

    #We combine user history and systemMessage and send it to LLM
    response = llm.invoke([sys_msg] + state["messages"])

    return {"messages": [response]}

def hardware_node(state: State):
    print("[BACKEND]: Hardware Engineer is processing packet ...")
    #We inject specific system Prompt for backend node
    sys_msg = SystemMessage(content="You are a Desktop Support Technician. You troubleshoot Monitor, cables, KVMs, RAM. You respond clearly step by step ")

    #We combine user history and SystemMessage and send ti to LLM
    response = llm.invoke([sys_msg] + state["messages"])

    return {"messages": [response]}

#4 CONTENT SWITCHING LOGIC
def traffic_triage(state: State):
    user_payload = state["messages"][-1].content
    decison = router_chain.invoke({"issue": user_payload})
    print(f"[VIP DISPATCHER]: Roting Packet -> {decison.destination}")
    return decison.destination

# TOPOLOGY AND PERSISTENCE 
builder = StateGraph(State)

builder.add_node("network_pool", network_node)
builder.add_node("hardware_pool", hardware_node)

builder.add_conditional_edges(START, traffic_triage)
builder.add_edge("network_pool", END)
builder.add_edge("hardware_pool", END)

#bind the persistency to the database(checkpointer)
conn = sqlite3.connect("bgyani_sessions.db", check_same_thread=False)
memory = SqliteSaver(conn)
app = builder.compile(checkpointer=memory)

# EXECUTION RUNNER
if __name__ == "__main__":
    print("---- BGYANI mutli agent router booted -----")

    #establishing the out sticky bit
    config = {"configurable": {"thread_id": "bgyani_ticket_001"}}

    #simulate user asking a question
    user_issue = "My dual 27-inch setup isn't working. The HDMI secondary screen is black."
    print(f"\nUser: {user_issue}")

    # Send the packet to graph
    events = app.invoke({"messages":[HumanMessage(content=user_issue)]}, config)

    # Print the final output whichever node is handling the traffic
    final_response = events["messages"][-1]

    #PAYLOAD CLEANER
    if isinstance(final_response.content, list):
        clean_text = "".join(block["text"] for block in final_response.content if isinstance(block, dict) and "text" in block)
    else:
        clean_text = final_response.content

    print(f"\n [A]: {clean_text}")

