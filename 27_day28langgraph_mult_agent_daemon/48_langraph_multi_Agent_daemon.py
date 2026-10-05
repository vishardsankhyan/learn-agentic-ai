import os
import sqlite3
import warnings
from dotenv import load_dotenv
from typing import Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMesage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.checkpoint.sqlite import SqliteSaver

warnings.filterwarnings("ignore", message=".*automatic function calling*.")

load_dotenv()

# 1. STATE and ROUTING BluePrint
class state(TypedDict):
    messages: Annotated[list, add_messages]

class RoutingTicket(BaseModel):
    destination: Literal["network_pool", "hardware_pool"] = Field(
        description="Route the user IT issue to correct backend node pool"
    )

# 2. Engine and Piplines (VIP Dispatcher)
llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)

parser = PydanticOutputParser(pydantic_object=RoutingTicket)
router_prompt = PromptTemplate(
    template="You are a strict IT routing dispatcher. Read the user issue and route it.\n{formal_instructions}\nUser Issue: {issue}",
    input_variables=['issue'],
    partial_variables={"formal_instructions": parser.get_format_instructions()}
)

#The LCEL Assembly line
router_chain = router_prompt|llm|parser

#3. Backend Server Pool
def network_node(state: State):
    print("\n[BACKEND]: Network Engine processing packet ...")
    sys_msg = SystemMessage(content="You are a Tier 3 Network Engine. You troubleshoot routing, BGP, Load Balancing, and DNS. Respond technically but concisely.")

    #Inject hidden system prompt
    response = llm.invoke([sys_msg]+state["messages"])
    return {"messages": [response]}

def hardware_node(state: State):
    print("\n[BACKEND]: Hardware Engineer processing packet ...")
    sys_msg = SystemMessage(content="You are a Desktop Support Technician. You troubleshoot Monitors, cables, KVMs, RAM. You respond clearly step by step.")

    #Inject hidden system prompt
    response = llm.invoke([sys_msg]+state["messages"])
    return {"messages": [response]}

#4. Content Switching Logic 
def traffic_triage(state: State):
    #Extract only the latest messages
    user_payload = state["messages"][-1].content

    #Send it to Pyantic router
    decision = router_chain.invoke({"issue": user_payload})

    print(f"\n[VIP DISPATCHER]: Routing Packet -> {decision.destination}")
    return decision.destination

#5. Topology and persistence
builder = StateGraph(State)

# Register the backend nodes
builder.add_node("network_pool", network_node)
builder.add_node("hardware_pool", hardware_node)

# Map the routing table
builder.add_conditional_edges(START, traffic_triage)
builder.add_edge("network_pool", END)
builder.add_edge("hardware_pool", END)

# Bind the persistent storage
conn = sqlite3.connect("bgyani_sessions.db", check_same_thread=False)
memory = SqliteSaver(conn)

# Compile the final application
app = builder.compile(checkpointer=memory)

#6. EXECUTION RUNNER (Daemon Loop)
if __name__ == "__main__":
    print("---- BGYANI Multi-Agent Helpdesk Booted -----")
    print("Type 'quit' to close the ticket.\n")

    # The Sticky Session ID
    config = {"configurable": {"thread_id": "bgyani_ticket_001"}}

    # The Continuous Loop
    while True:
        user_issue = input("User: ")

        # Graceful shutdown
        if user_issue.lower() in ["quit", "exit"]:
            print("Closing ticket. Goodbye!")
            break

        # Send the packet to the graph
        events = app.invoke({"messages": [HumanMessage(content=user_issue)]}, config)

        # Extract the final AI message object
        raw_packet = events["messages"][-1]

        # Clean payload (Strips Gemini JSON wrappers if present)
        if isinstance(raw_packet.content, list):
            clean_payload = raw_packet.content[0]['text']
        else:
            clean_payload = raw_packet.content

        print(f"\n[AI]:\n{clean_payload}\n")
        print("-" * 50 + "\n")
    
