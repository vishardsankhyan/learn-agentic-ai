import os
import warnings
from dotenv import load_dotenv
from typing import Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel , Field

from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage
from langchain_google_genai import GoogleGenerativeAI

#Standardized Routing Import
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

warnings.filterwarnings("ignore", message=".*automatic function calling.*")

load_dotenv()

#1. DEFINE THE STATE (The packet)
class State(TypedDict):
    messages: Annotated[list, add_messages]

#2. THE PYDANTIC GUARDRAIL (The CS policy)
#We force LLM to return only 2 output nd no conversation
class TicketRouter(BaseModel):
    destination: Literal["netwokr_pool","hardware_pool"] = Field( 
        description="Route ticket correctly to the backend pool.."
    )

#3. INIIALIZE THE LLM
llm = GoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)

#We bind the pydantic to LLM to act as a purely routing engine instead of the conversation LLM bot
parser = PydanticOutputParser(pydantic_object=(TicketRouter))


prompt = PromptTemplate(
    template="You are a strict IT routing dispatcher. Read the user's issue and route it.\n{format_instructions}\nUser Issue: {issue}",
    input_variables=["issue"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

#Our Lock in pipeline : Packet -> Prompt -> LLM -> Parser Validation
router_chain = prompt | llm | parser

#4. DEFINE THE BACKEND POOL 
def network_node(state: State):
    print("[BACKEND]:  Network Team handling the packet (IPs, DNS, Load Balancing).")
    return {"messages": [("ai", "Network issue resolved.")]}

def hardware_node(state: State):
    print("[BACKEND]: Hardware Team handling the packet (Monitors, RAM, Laptops).")
    return {"messages": [("ai", "Hardware issue resolved.")]}

#5. DEFINE THE CONTENT SWITCHING LOGIC (The Conditional Edge)
def traffic_triage(state: State):
    user_payload = state["messages"][-1].content

    # We send the payload to the router LLM
    # Thanks to Pydantic, 'decision.destination' is gurantted to be clean string
    descison = router_chain.invoke({"issue": user_payload})
    print(f"[DISPATCHER]: Payload is sent to LLM .... Routin to {descison.destination}")

    return descison.destination

#6. BUILD THE GRAPH TOPOLOGY
builder = StateGraph(State)

#Add the backend pool
builder.add_node("network_pool", network_node)
builder.add_node("hardware_pool", hardware_node)

#The START edge node is sending traffic to Our Conditional Logic
builder.add_conditional_edges(START, traffic_triage)

#Terminate after hitting the backend
builder.add_edge("network_pool", END)
builder.add_edge("hardware_pool", END)

#compile
app = builder.compile()

#7. EXECUTION
if __name__ == "__main__":
    print("-------BGYANI Tier 1 dispatch booted---------")

    # Test 1: A network payload
    test_1 = "My BGP neighbor relationship just dropped and I can't reach the subnet."
    print(f"\nUser: {test_1}")
    app.invoke({"messages": [HumanMessage(content=test_1)]})

    # Test 2: A hardware payload
    test_2 = "My secondary 27-inch monitor isn't receiving an HDMI signal from my laptop."
    print(f"\nUser: {test_2}")
    app.invoke({"messages":[HumanMessage(content=test_2)]})


    