import os
import asyncio
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI 
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv()

#1. INITIALIZE VectorDB
print("[SYSTEM]: Connecting to the ChromaDB")
embeddings=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vector_db = Chroma(
    persist_directory="./bgyani_runbook_db",
    embedding_function=embeddings
)

#2. Agent building

@tool
def search_it_runbook(query: str) -> str:
    """ 
    It searches in IT RunBook, netScaler configuration, netscaler architecture.
    Use this tool when user ask for the troubleshooting and the configuration assistance or asked about infrastructure policy.
    """

    results = vector_db.similarity_search(query, k=2)

    if not results:
        return "The query was not found in the search book , please raise a seperate query"

    else:
        formatted_content = []
        for idx, doc in enumerate(results,1):
            formatted_content.append(f"------document id:{idx}\n")
            formatted_content.append(f"{doc.metadata.get('source', 'Unknown')}\n")
            formatted_content.append(f"{doc.page_content}\n")

    return "".join(formatted_content)

#3. Build teh Triage
async def bgyani_triage():
    print("[SYSTEM]: Invoking the BGYANI_ TRIAAGE")

    # LLM Defiantion
    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.0)

    # tool defination
    tools = [search_it_runbook]

    #Defining the personna : system prompt:
    system_prompt =" You are BGYANI TRIAGE, IT specialist who is expert. You have access to the search_it_runbook tool to look into technical docs before answering. If you don't find the answer you say need to escalate it"
       
    #Compile the Graph
    agent_executor = create_react_agent(
       llm,
       tools,
    )

    #binding the agent information and generating the tool json file
    #agent = create_tool_calling_agent(llm,tools,prompt)

    #Agent Execution: ReAct while loop
    #agent_execution = AgentExecutor(agent=agent, tools=tools, verbose=False)

    #Run a test ticket
    ticket = "A user is getting VPN error 809, how do I fix it"

    inputs = {
        "messages": [
            ("system", system_prompt),
            ("user", ticket)
        ]
    }


    print(f"\n[NEW TICKET]: {ticket}")

    result = await agent_executor.ainvoke(inputs)

    print(f"The result is : {result['messages'][-1].content}")

if __name__ == "__main__":
    asyncio.run(bgyani_triage())

