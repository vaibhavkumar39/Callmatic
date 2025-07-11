@app.post("/process_speech", response_class=PlainTextResponse)
async def process_speech(SpeechResult: str = Form(...)):
    response = VoiceResponse()

    if SpeechResult.strip():
        lang = detect_language(SpeechResult)
        print("Detected language:", lang)

        voice, language_code = {
            "hi": ("Polly.Raveena", "hi-IN"),
            "hinglish": ("Polly.Raveena", "en-IN"),
            "en": ("Polly.Raveena", "en-IN")
        }.get(lang, ("Polly.Joanna", "en-IN"))


        if os.path.exists("vector_db"):
            qa_chain = load_qa_chain()
            reply = qa_chain.run(SpeechResult)
        else:
            reply = ask_bot(SpeechResult, language=lang)

        response.say(reply, voice=voice, language=language_code)

        with open("transcript.txt", "a", encoding="utf-8") as f:
            f.write(f"User ({lang}): {SpeechResult}\nBot: {reply}\n\n")

    else:
        response.say("Sorry, I didn't catch that.", voice="Polly.Raveena", language="en-IN")

    response.redirect("/voice")
    return str(response)
