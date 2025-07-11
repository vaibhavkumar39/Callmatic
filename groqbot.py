import os
from groq import Groq
from dotenv import load_dotenv
from langdetect import detect
import re

load_dotenv()

client = Groq(api_key="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")

def ask_bot(prompt: str, language: str = "en") -> str:
    if language == "hi":
        system_prompt = (
            "You are a helpful voice assistant for technical and general questions. If the user speaks Hindi, reply in Hinglish (Hindi in Roman script) like an Indian assistant."
        )
    elif language == "en":
        system_prompt = (
            "You are a helpful assistant that answers technical and programming questions in English briefly and clearly."
        )
    else:
        system_prompt = (
            "You are a helpful assistant that answers technical and general questions in Hinglish (Hindi in Roman script)."
        )

    try:
        chat_completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100  
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error from Groq API: {e}"


def detect_language(text: str) -> str:
    try:
        lang = detect(text)

        if lang == "hi":
            return "hi"
        elif lang == "en":
            hindi_words = hindi_words = ["kya", "hai", "kaise", "kyun", "nahi", "batao", "karna","mujhe", "tum", "acha", "samjha", "bolo", "kar", "tha", "thi", "hota"]
            for word in hindi_words:
                if re.search(rf"\b{word}\b", text.lower()):
                    return "hinglish"
            return "en"
        else:
            return "en"
    except Exception as e:
        print(f"Language detection error: {e}")
        return "en"
