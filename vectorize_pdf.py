import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()
os.environ["GROQ_API_KEY"] = "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"

def vectorize_pdf(pdf_path: str, db_path: str = "vector_db"):
    print("Loading and splitting PDF...")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    print("Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("Creating FAISS vectorstore...")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    print(f"Saving vectorstore to `{db_path}`...")
    vectorstore.save_local(db_path)
    print("Vectorization complete.")

if __name__ == "__main__":
    vectorize_pdf("python.pdf")
