import os
from langchain_community.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

def build_vector_db(pdf_path: str, db_path: str = "vector_db"):
    print("🔍 Loading PDF:", pdf_path)
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    print("✂️ Splitting text...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    print("🧠 Generating embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("💾 Building and saving vector store...")
    vectorstore = FAISS.from_documents(chunks, embedding=embeddings)
    vectorstore.save_local(folder_path=db_path)

    print(f"✅ Vector DB saved to: {db_path}")

if __name__ == "__main__":

    build_vector_db("file name -----------------------------------------.pdf")
