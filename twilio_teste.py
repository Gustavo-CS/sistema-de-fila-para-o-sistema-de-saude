
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_SMS_NUMBER = os.environ.get("TWILIO_SMS_NUMBER") 


client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def enviar_sms(para, mensagem):
    message = client.messages.create(
        body=mensagem,
        from_=TWILIO_SMS_NUMBER,
        to=para  # Ex: +5511999999999
    )
    return message.sid
