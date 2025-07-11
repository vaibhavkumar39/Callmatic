from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
from groqbot import detect_language, ask_bot
from groqbot_with_pdf import load_vector_db
from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()
app = FastAPI()
vector_db = None
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.on_event("startup")
def startup_event():
    global vector_db
    print("Loading PDF Vector DB...")
    vector_db = load_vector_db()
    print("Vector DB loaded successfully.")

@app.post("/voice", response_class=PlainTextResponse)
async def voice(request: Request):
    response = VoiceResponse()
    
    gather = Gather(
        input="speech",
        action="/process_speech",
        method="POST",
        timeout=5,
        speech_timeout="auto", 
        speech_model="default",
        language="hi-IN",         
        barge_in=True
    )

    gather.say("Hi! What would you like to say?", voice="Polly.Aditi", language="en-IN")
    response.append(gather)

    response.say("I didn't hear anything. Please try again.", voice="Polly.Aditi", language="en-IN")
    response.redirect("/voice")
    return str(response)

@app.post("/process_speech", response_class=PlainTextResponse)
async def process_speech(SpeechResult: str = Form(...)):
    response = VoiceResponse()

    if SpeechResult.strip():
        lang = detect_language(SpeechResult)
        print("Detected language:", lang)

        voice, language_code = {
            "hi": ("Polly.Aditi", "en-IN"),
            "hinglish": ("Polly.Aditi", "en-IN"),
            "en": ("Polly.Aditi", "en-IN")
        }.get(lang, ("Polly.Aditi", "en-IN"))

        trigger_keywords = ["python", "programming", "function", "loop", "variable"]
        lower_text = SpeechResult.lower()

        if any(keyword in lower_text for keyword in trigger_keywords):
            print("Trigger word detected, answering from PDF using Groq RAG...")

            relevant_docs = vector_db.similarity_search(SpeechResult, k=3)
            context = "\n\n".join(doc.page_content for doc in relevant_docs)

            prompt = f"""
            Answer the following user question based only on the context below. Keep your response professional, warm, and feminine in tone.
            Use full potential to understand and reply in same language as user asked.

            Context:
            {context}

            User’s Question:
            {SpeechResult}

            Answer:
            """
            

            instruction_prompt = f"""
            You are a smart, professional female Indian voice assistant. Your tone is warm, clear, and respectful — like a well-trained female customer care executive in India.

            Goal:
            Answer the user's question based ONLY on the context provided. Understand their language and tone deeply, and respond in a short, natural, human-like way.

            Communication Style:
            - Speak in a short, **spoken-sounding way** (like a phone call), not like a textbook.
            - Answer in **under 3 sentences**, unless a **list** is asked (e.g., 5 items, 10 tools, 20 languages).
            - If user asks for a list (top 10, 5 examples, etc), give **exactly that number**, with **each item on a new line**, and **no bullet points or numbering**.
            - Grammar must be very **easy and natural**, like how people actually talk.

            Language Rules:
            - If the user asks in **Hindi or Hinglish**, reply in Hindi — use **Hindi script** for common words, and **English** for technical/global terms like Python, modules, Google.
            - **Do not mix both languages** in one sentence unless it's natural (e.g., "Python का loop").
            - Never write both translations (e.g., don’t say "Google Ads यानी Google के ads").
            - If the user speaks in full **English**, reply in clear, casual **spoken English**.

            Gender Consistency:
            - Always use **feminine grammar**, like: "बता सकती हूँ", "कर रही हूँ", "ready हूँ", etc.
            - Never use masculine terms like "बता सकता हूँ", "भाई", "यार", "अबे", etc.

            Soft Handling for Unknowns:
            - If something is not in the context, NEVER say "I don’t know".
            - Say something polite like: "इस बारे में मुझे अभी exact जानकारी नहीं है, लेकिन मैं check करके बताने की कोशिश कर सकती हूँ।"

            Knowledge Completion:
            - Use your intelligence and general world knowledge to answer well — **complete the answer even if some data is missing from the context**.
            and always give short answers.

            Summary:
            Speak like a kind, professional, and intelligent Indian female voice assistant. Be helpful, human, and accurate. Always answer in the same language the user asked — use **Hindi script for Hindi**, **English for technical terms**, and **spoken-style grammar** throughout.

            Now, based only on this context:

            Context:
            {context}

            User’s Question:
            {SpeechResult}

            Answer:
            """

            if any(x in SpeechResult.lower() for x in ["bataye", "batao", "list", "top", "5", "10", "examples"]):
                instruction_prompt += "\nYou must give a complete list with the exact number of items if user asks."

            try:
                chat_completion = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": instruction_prompt }, #"You are a helpful assistant answering based on the given context in whatever language it is asked but professionally."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=8000
                )
                reply = chat_completion.choices[0].message.content.strip()
            except Exception as e:
                reply = f"Error answering from PDF: {e}"
        else:
            if lang == "hi":
                lang = "hinglish"

            reply = ask_bot(SpeechResult, language=lang)

        print("Reply:", reply)
        response.say(reply, voice=voice, language=language_code)

        with open("transcript.txt", "a", encoding="utf-8") as f:
            f.write(f"User ({lang}): {SpeechResult}\nBot: {reply}\n\n")
    else:
        response.say("Sorry, I didn't catch that.", voice="Polly.Aditi", language="en-IN")

    response.redirect("/voice")
    return str(response)


# from fastapi import FastAPI, Request, Form
# from fastapi.responses import PlainTextResponse
# from twilio.twiml.voice_response import VoiceResponse, Gather
# from groqbot import detect_language, ask_bot
# from groqbot_with_pdf import load_qa_chain
# from dotenv import load_dotenv

# load_dotenv()
# app = FastAPI()
# qa_chain = None

# @app.on_event("startup")
# def startup_event():
#     global qa_chain
#     print("Loading QA Chain from PDF...")
#     qa_chain = load_qa_chain()
#     print("QA Chain loaded successfully.")

# @app.post("/voice", response_class=PlainTextResponse)
# async def voice(request: Request):
#     response = VoiceResponse()
    
#     gather = Gather(
#         input="speech",
#         action="/process_speech",
#         method="POST",
#         timeout=5,
#         speech_timeout="auto", 
#         speech_model="default",
#         language="hi-IN",         
#         barge_in=True
#     )

#     gather.say("Hi! What would you like to say?", voice="Polly.Aditi", language="en-IN")
#     response.append(gather)

#     response.say("I didn't hear anything. Please try again.", voice="Polly.Aditi", language="en-IN")
#     response.redirect("/voice")
#     return str(response)

# @app.post("/process_speech", response_class=PlainTextResponse)
# async def process_speech(SpeechResult: str = Form(...)):
#     response = VoiceResponse()

#     if SpeechResult.strip():
#         lang = detect_language(SpeechResult)
#         print("Detected language:", lang)

#         voice, language_code = {
#             "hi": ("Polly.Aditi", "en-IN"),
#             "hinglish": ("Polly.Aditi", "en-IN"),
#             "en": ("Polly.Aditi", "en-IN")
#         }.get(lang, ("Polly.Aditi", "en-IN"))

#         trigger_keywords = ["python", "programming", "function", "loop", "variable"]
#         lower_text = SpeechResult.lower()

#         if any(keyword in lower_text for keyword in trigger_keywords):
#             print("Trigger word detected, using PDF QA chain...")
#             result = qa_chain.invoke({"query": SpeechResult})
#             reply = result["result"]
#         else:
#             # Force Hindi into Hinglish response
#             if lang == "hi":
#                 lang = "hinglish"

#             reply = ask_bot(SpeechResult, language=lang)


#         print("Reply:", reply)
#         response.say(reply, voice=voice, language=language_code)

#         with open("transcript.txt", "a", encoding="utf-8") as f:
#             f.write(f"User ({lang}): {SpeechResult}\nBot: {reply}\n\n")
#     else:
#         response.say("Sorry, I didn't catch that.", voice="Polly.Aditi", language="en-IN")

#     response.redirect("/voice")
#     return str(response)
