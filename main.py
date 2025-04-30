from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{os.getenv('PHONE_NUMBER_ID')}/messages"
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")

class MessageRequest(BaseModel):
    to: str
    message: str

@app.post("/send-message/")
async def send_whatsapp_message(payload: MessageRequest):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data =     { "messaging_product": "whatsapp"
     , "to": payload.to,
     "type": "template",
     "template": 
         {
             "name": "hello_world",
             "language": { "code": "en_US" } } }

    async with httpx.AsyncClient() as client:
        response = await client.post(WHATSAPP_API_URL, json=data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=response.text)

    return {"status": "message sent", "response": response.json()}


