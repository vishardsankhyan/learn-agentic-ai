import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from typing import TypedDict
from langgraph.graph import StateGraph , END

load_dotenv()

#1. DEFINE THE STATE
#This dictates exactly what data passed between our nodes
class TicketState(TypedDict):
    ticket_text: str
    category: str
    final_resolution: str


# Initiailize the LLM
llm = GoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.0)

#2. Defining the nodes (Backend Services)
# Every Node is the python function that takes the current state
# does a piece of work and return the updated state.

def triage_operator_node(state: TicketState):
    print("[ROUTER] Analyzing the incoming ticket ....")
    prompt = f"""
    Read the following IT ticket. Categorize it into one of the three words:
    'network', 'hardware' or 'software'. Do not output anything else.
    Ticket:{state['ticket_text']}   
    """

    #Ask LLM to categorize it
    response = llm.invoke(prompt)
    category = response.strip().lower()
    print(f"[ROUTER] Ticket classified as -> {category.upper()}")

    #Update the state with new category
    return {'category': category}

def network_specialist_node(state: TicketState):
    print("[NETWORK NODE]: Processing...")
    return {"final_resolution": "Action: Escalated to L3 Network Team. Checking ADC logs and VPN firewall rules."}

def hardware_specialist_node(state: TicketState):
    print("[HARDWARE NODE]: Processing...")
    return {"final_resolution": "Action: Escalated to Datacenter Ops. Dispatching technician for physical inspection."}

def software_specialist_node(state: TicketState):
    print("[SOFTWARE NODE]: Processing...")
    return {"final_resolution": "Action: Escalated to App Support. Analyzing application crash dumps."}

#3. DEFINING THE ROUTNG LOGIC
def route_ticket(state: TicketState):
    #This function reads the state and tells graphs to which node to follow next
    return state["category"]

#4. BUILD THE GRAPH (The Architecture)
builder = StateGraph(TicketState)

#Add nodes to the graph 
builder.add_node("router", triage_operator_node)
builder.add_node("network", network_specialist_node)
builder.add_node("hardware", hardware_specialist_node)
builder.add_node("software", software_specialist_node)

#Set the entry point
builder.set_entry_point("router")

#Add a conditional edges
builder.add_conditional_edges(
    "router" , # The node we are routing from
    route_ticket, # The function that decide where to go
    {
        "network": "network",
        "hardware": "hardware",
        "software": "software"
    }

)

#Terminate the graph after the specialist answer
builder.add_edge("network", END)
builder.add_edge("hardware", END)
builder.add_edge("software", END)

#compile the graph into a runable application
triage_graph = builder.compile()

#5. EXECUTION
if __name__ == "__main__":
    test_ticket = "My monitor won't turn on and the USB-C display cable seems frayed."
    print(f"\n[NEW TICKET]: {test_ticket}\n")
    
    # Inject the initial state
    initial_state = {"ticket_text": test_ticket}

    #Run the Graph 
    result = triage_graph.invoke(initial_state)

    print(f"\n[FINAL OUTPUT]: {result['final_resolution']}\n")