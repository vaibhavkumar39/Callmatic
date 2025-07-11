import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_groq import ChatGroq
# from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate
# from dotenv import load_dotenv
# load_dotenv()


def load_vector_db(db_path="vector_db"):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.load_local(
        folder_path=db_path,
        embeddings=embeddings,
        allow_dangerous_deserialization=True  
    )

# def load_qa_chain():
#     vectorstore = FAISS.load_local(
#         folder_path="vector_db",
#         embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
#         allow_dangerous_deserialization=True
#     )

#     llm = ChatGroq(
#         model="llama3-70b-8192",
#         api_key=os.getenv("GROQ_API_KEY")
#     )

#     prompt_template = """
#     You are a knowledgeable and polite assistant.

#     Listen to the call and detect language with full potential and reply accordingly as told below.
#     Remember your hindi and hinglish should be perfect for the model to say so it get a per.

#     You must ALWAYS reply in the language that the question is asked in:
#     - If the user asks in Hindi, reply only in Hinglish with proper accent.
#     - If the user asks in English, reply only in English.
#     - If the user asks in Hinglish (Hindi in English letters), reply in Hinglish.

#     and remember if you are doing it in hindi it should be in proper accent in hinglish (Hindi in English letters).

#     Your reply must be **very short and to the point**, like a voice assistant.
#     Do not exceed 3 short sentences. Keep it brief enough to be spoken in under 4 seconds.

#     Use only the context provided to answer the question.

#     Context:
#     {context}

#     Question:
#     {question}

#     Short Answer in the same language:"""

#     prompt = PromptTemplate(
#         input_variables=["context", "question"],
#         template=prompt_template,
#     )

#     return RetrievalQA.from_chain_type(
#         llm=llm,
#         retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
#         return_source_documents=True,
#         chain_type_kwargs={"prompt": prompt}
#     )