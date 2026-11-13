# ingestion.py
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone
from pinecone import Pinecone as PineconeClient
# =====================
# CONFIG
# =====================
INDEX_NAME = "medicalbot"

# =====================
# LOAD DOCUMENTS
# =====================
def load_documents():
    loader = PyPDFDirectoryLoader("documents/")
    return loader.load()

# =====================
# SPLIT DOCUMENTS
# =====================
def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=50
    )
    return splitter.split_documents(docs)

# =====================
# INGESTION
# =====================
def run_ingestion():
    print("📄 Loading PDFs...")
    docs = load_documents()

    print("✂️ Splitting documents...")
    chunks = split_docs(docs)

    print("🧠 Loading embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("⬆️ Uploading vectors to Pinecone (ONE TIME)...")
    Pinecone.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=INDEX_NAME
    )

    print("✅ INGESTION COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    run_ingestion()
