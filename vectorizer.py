import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

def load_and_split_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    return chunks

def embed_and_store(chunks):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore, embeddings

if __name__ == "__main__":
    os.environ["GROQ_API_KEY"] = "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"

    pdf_path = "python.pdf"

    print("Loading and splitting PDF...")
    chunks = load_and_split_pdf(pdf_path)

    print("Embedding and storing vectors...")
    vectorstore, embeddings = embed_and_store(chunks)

    # print(f"\n Number of vectors stored: {vectorstore.index.ntotal}")
    example_vector = embeddings.embed_query("Test query")
    # print(f"Example embedding dimension: {len(example_vector)}")

    vectorstore.save_local("vector_db")
    print(" FAISS vectorstore saved to ./vector_db")

    llm = ChatGroq(model="llama3-70b-8192") 

    prompt_template = """
    You are a helpful assistant. Answer the question below based only on the provided context.
    Always reply in the **same language** the question is asked — use Hinglish if the question is in Hinglish, Hindi if in Hindi, or English if in English.
    Context:
    {context}

    Question:
    {question}

    Answer:"""

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=prompt_template,
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    query = input("Ask question: ")
    result = qa_chain.invoke({"query": query})

    print("\n Groq Answer:")
    print(result["result"])