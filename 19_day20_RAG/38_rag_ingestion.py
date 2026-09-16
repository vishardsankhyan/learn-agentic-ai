import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

#Load GEMINI API KEY
load_dotenv()

#1. Initialize the Embedding Model
#This convert english text into 768 dimentional mathemetical cordinates
print("[SYSTEM]: Initialize the Embedding Model ...")
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

#2. prepare a static Run book
#We tage MetaData for future data filetering

raw_runbooks = [
    Document(
        page_content="NetScaler ERR_503 on auth_backend: This occurs when the AAA vServer cannot reach the LDAP/RADIUS server. Check the NSIP routing table and firewall port 389/636.",
        metadata={"category": "netscaler", "type": "auth", "severity": "high"}
    ),
    Document(
        page_content="STP Loop Detected: Spanning Tree Protocol failure causing broadcast storms. Immediately shut down the redundant port on the edge switch and verify BPDU guard configuration.",
        metadata={"category": "switching", "type": "layer2", "severity": "critical"}
    ),
    Document(
        page_content="High Availability Split Brain: Both HA nodes claim to be Primary. Verify the heartbeat network on interface 0/1 and check for MAC address conflicts in the hypervisor.",
        metadata={"category": "netscaler", "type": "ha_cluster", "severity": "critical"}
    )
]

#3. Ingest data into ChromaDB
print("[SYSTEM]: Ingesting runbook into the local vector DB")

vector_db = Chroma.from_documents(
    documents=raw_runbooks,
    embedding=embeddings,
    persist_directory="./bgyani_runbook_db" #Creates a local folder to store data
)

print("[SYSTEM]: Ingestion complete and data is availalble ./bgyani_runbook_db")

#4.Test the Semantic search 
#The query is in normal english language
user_query="Users can't login, it seems Loadbalacer is not able to talk to active directory"

print(f"[Query]: {user_query}")
print("[SYSTEM]: search for the closest mathematical match....")

#k=1 means returning the most relavant single chunk.
results = vector_db.similarity_search(user_query, k=1)

for result in results:
    print(f"--- Match Found(Category: {result.metadata['category']})")
    print(f"--- RUNBOOK Steps: {result.page_content}\n")

