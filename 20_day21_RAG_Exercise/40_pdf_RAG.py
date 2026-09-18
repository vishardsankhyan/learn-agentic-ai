import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings 

load_dotenv()

pdf_path = "./books.pdf"
print(f"[SYSTEM]: loading pdf from {pdf_path}")

loader = PyPDFLoader(pdf_path)
raw_pdf_docs = loader.load()

#PyPDF treats every page as a single document initially
print(f"[SYSTEM]: total number of pages {len(raw_pdf_docs)}")

#2. The Splitter: chunking Page into semantic chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

print(f"[SYSTEM]: Splitiing page into chunk ...")
chunked_doc = text_splitter.split_documents(raw_pdf_docs)
print(f"[DEBUG]: Successfully split into {len(chunked_doc)} Document chunk")

print("\n[SYSTEM]: EMbedding chunks and creting ephermeral DB ....")
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

vector_db = Chroma.from_documnets(
    documents=chunked_doc,
    embedding=embeddings
)

# The TEST

query = "What is the main topic of this doc"

results = vector_db.similarity_search(query, k=1)

for i , result in enumerate(results, 1):
    print(f"\n--- BEST MATCH ---")
    # Notice the amazing metadata PyPDFLoader gives us automatically!
    print(f"Source File: {result.metadata['source']}")
    print(f"Found on Page: {result.metadata['page']}") 
    print(f"Content Snippet: {result.page_content[:250]}...")