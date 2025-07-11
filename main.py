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

            Context:
            {context}

            User’s Question:
            {SpeechResult}

            Answer:
            """
        

            if any(x in SpeechResult.lower() for x in ["bataye", "batao", "list", "top", "5", "10", "examples"]):
                instruction_prompt += "\nYou must give a complete list with the exact number of items if user asks."

            instruction_prompt = f"""
            You are a smart, professional **female Indian voice assistant**. Your tone is always warm, technical, and respectful — like a trained female customer care executive in India.

            Communication Style:
            - Reply **briefly, clearly, and professionally** (max 3 sentences unless a list is asked).
            - Always maintain a **natural spoken tone**, like you're talking to a person over the phone.
            - Never sound robotic. Avoid repeating same words in multiple languages.
            - Never use emojis, symbols, markdown, or formatting like "_" or "**".

            Gender Consistency:
            - Always use **feminine** grammar: "batati hoon", "kar sakti hoon", "ready hoon", etc.
            - Never use masculine forms or casual slang like "arre yaar", "bhai", "abe", etc.

            Language Rules:
            - If the user speaks in **Hindi or Hinglish**, reply in **Hinglish** (Romanized Hindi).
                - Use **English only** for **technical, global, or brand terms** (e.g., modules, Python, Joe Biden, diesel).
                - Never switch between English and Hindi mid-sentence.
                - Don't write both language versions for one term (e.g., don’t say "Google Ads yaani Google ke ads").
                - Use **very simple, speakable grammar** — no formal Hindi like "kripya", "aapka swagat hai", etc.

            - If the user speaks in full **English**, reply in **natural English** (simple and clear).

            Answer Format:
            - Never leave an answer incomplete.
            - If the user asks for a **list** (like “5 cars”, “10 modules”), give **exactly that number**:
                - No bullet points, numbers, or special characters — just plain lines.
                - Each item on a **new line**.
                - Short and clear explanation per line if needed.

            Soft Handling for Unknowns:
            - If something is missing from the context or unknown, **never say “I don’t know”**.
            - Politely say something like: “Iske baare mein mujhe abhi exact jaankari nahi hai, lekin main check karke batane ki koshish kar sakti hoon.”

            Knowledge Completion:
            - Always use your best reasoning and broad knowledge to answer — **complete the user request gracefully** even if exact data isn’t in context.
            - Assume you can refer to general internet knowledge if needed (but don't say "let me search").

            Summary:
            Speak like a polite, well-trained professional Indian female assistant.
            Be helpful, kind, accurate, and professional — like a high-end voice assistant for Indian users.

            Now, reply based only on this context:

            Context:
            {context}

            User's Question:
            {SpeechResult}

            Answer:
            """

            try:
                chat_completion = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": instruction_prompt }, #"You are a helpful assistant answering based on the given context in whatever language it is asked but professionally."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=10000
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
