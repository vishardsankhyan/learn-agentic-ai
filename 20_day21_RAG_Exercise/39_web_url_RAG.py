import os
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

#1. loader 
target_url = "https://docs.netscaler.com/en-us/citrix-adc/current-release/getting-started-with-citrix-adc"
print(f"[SYSTEM]: Scraping {target_url}...")

loader = WebBaseLoader(target_url)
raw_web_docs = loader.load()

print(f"[DEBUG]: Download {len(raw_web_docs)} massive documents.")
print(f"[DEBUG]: Total Charaters: {len(raw_web_docs[0].page_content)}")

#2. Text Chopper
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

print("\n[SYSTEM]: Splitting document into smaller chunk ...")
chunked_docs = text_splitter.split_documents(raw_web_docs)

print(f"\n[DEBUG]: Successfully split into {len(chunked_docs)} indivisual Document chunk")

#3. INGESTION
print("\n[SYSTEM]: Embedding chunks and building ChromaDB ....")
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

tiny_chunk_list = chunked_docs[:5]
#Running in-memory for testing
vector_db = Chroma.from_documents(
    documents=tiny_chunk_list,
    embedding=embeddings
)

#4 THE TEST:
query = "What is deafult IP to access management GUI"
print(f"\n[USER TICKET]: {query}")

#fetch the 2 closed chuncks
results = vector_db.similarity_search(query, k=2)

for i, result in enumerate(results, 1):
    print(f"\n --- MATCH {i} ---")
    print(f"\n SOURCE URL: {result.metadata['source']}")
    #print first 250 characters
    print(f"Content Snippet: {result.page_content[:250]}...")


