import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

mini_runbook = [
    Document(
        page_content="VPN Error 809: L2TP/IPsec connection failed because the security layer could not negotiate parameters. Fix: Check UDP ports 500 and 4500 on the edge firewall.",
        metadata={"category": "vpn", "severity": "medium"}
    ),
    Document(
        page_content="NetScaler Gateway 1053: User authentication failed due to expired Active Directory password or locked account. Fix: Reset AD credentials via the self-service portal.",
        metadata={"category": "netscaler", "severity": "high"}
    )
]

#Vector DataBase
print("[SYSTEM]: Data ingestion in ephemeral ChromaDB")
vector_db = Chroma.from_documents(
    documents=mini_runbook,
    embedding=embeddings
)

#Semantic Search
query = "Remote workers are complaining their tunnels are dropping. They mentioned something about security negotiation."

print(f"[USER INPUT]: {query}")
print("[SySTEM]: system is checking the cosine similarity")

results = vector_db.similarity_search(query, k=1)

for result in results:
    print(f"\n --> BEST MATCH(Category:{result.metadata['category']})")
    print(f"\n --> RUNBOOK_Entry: {result.page_content}")

print(f"\n\n\n [RESULT]: {results}")Hell