import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

def calling_function():
    account_sid = os.getenv("account_sid")
    auth_token = os.getenv("auth_token")
    twilio_number = os.getenv("twilio_number")
    to_number =  "+919870236078" #"+919773903654" #
    ngrok_url = os.getenv("ngrok_url")
    client = Client(account_sid, auth_token)
    call = client.calls.create(
        from_=twilio_number,
        to=to_number,
        url=f"{ngrok_url}/voice"
    )
    print("Calling... SID:", call.sid)
if __name__ == "__main__":
    calling_function()