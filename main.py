from fastapi import FastAPI, UploadFile, File, HTTPException,Request,Query
import httpx
import os
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO
from tables import WhatsAppMessageLog
from database import SessionLocal
from datetime import datetime, timezone
import json
from models import *

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
ACCESS_TOKEN = "Bearer EABhUZAQcZAwSQBO3naKxLr0vFA81k6ul78PFsD4qOObsQ2v8M7miFBW01IoPDc26h91rm5KaiAWWjcv7aSN9V42ZBxJOnn2rldFbb61dcnLOnAlbEkvQ6DpbkJvyR2PoonNfLvSOsOBp5F5GwA77McY2mupv9ZCotmf8HquQlqXCqQBJUf5T01hclg9e8GN1Uq9znCx6yWWTuJfiQUoC40Yz64u2ZAdhkJKkYhgXdTyER"


# @app.post("/send-message/")
# async def send_whatsapp_message(payload: MessageRequest):
#     headers = {
#         "Authorization": f"Bearer {ACCESS_TOKEN}",
#         "Content-Type": "application/json",
#     }

#     data = {
#         "messaging_product": "whatsapp",
#         "to": payload.to,
#         "type": "template",
#         "template": {"name": "hello_world", "language": {"code": "en_US"}},
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.post(WHATSAPP_API_URL, json=data, headers=headers)

#     if response.status_code != 200:
#         raise HTTPException(status_code=500, detail=response.text)

#     return {"status": "message sent", "response": response.json()}



@app.post("/send-message-form/")
async def send_whatsapp_message_form(payload: SingleMessageRequest):
    headers = {
        "Authorization": f"{ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    print(headers)
    data = {
        "messaging_product": "whatsapp",
        "to": payload.phone_number,
        "type": "template",
        "template": {"name": "hello_world", "language": {"code": "en_US"}},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(WHATSAPP_API_URL, json=data, headers=headers)

    # if response.status_code != 200:
    #     raise HTTPException(status_code=500, detail=response.text)

    return {"status": "message sent", "response": response.json(),"data":payload}



@app.post('/send_bulk_messages')
async def send_bulk_messages(file: UploadFile = File(...)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="File must be an .xlsx Excel file")

    content = await file.read()
    df = pd.read_excel(BytesIO(content))

    required_columns = {"Full Name", "Mobile No", "location", "qualification"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"Missing required columns: {required_columns}")

    results = []
    session = SessionLocal()
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    for _, row in df.iterrows():
        to = str(row["Mobile No"]).strip()
        if not to.startswith("+"):
            to = "91" + to 
        name = str(row["Full Name"])
        location = str(row["location"])
        qualification = str(row["qualification"])
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {"name": "hello_world", "language": {"code": "en_US"}},
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(WHATSAPP_API_URL, json=data, headers=headers)
        results.append({
            "to": to,"status":response.status_code,"response":response.text
        })
        log = WhatsAppMessageLog(
            phone_number=to,
            full_name=name,
            location=location,
            qualification=qualification,
            status_code=response.status_code,
            response_text=response.text,
            sent_at=datetime.now(timezone.utc)
        )
        session.add(log)
        session.commit()
    return {'res':results}



@app.get('/get_logs')
def method_get_logs():
    session = SessionLocal()
    logs = session.query(WhatsAppMessageLog).order_by(WhatsAppMessageLog.sent_at.desc()).all()
    return [
        {
            "id": log.id,
            "phone_number": log.phone_number,
            "full_name": log.full_name,
            "location": log.location,
            "qualification": log.qualification,
            "status_code": log.status_code,
            "response_text": log.response_text,
            "sent_at": log.sent_at.isoformat()
        }
        for log in logs
    ]
    
    
    
@app.post('/webhook')
async def method_webhook_call(request: Request):
    body = await request.json()
    print("📨 Incoming webhook message:", json.dumps(body, indent=2))    
    return {}



@app.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(default=None, alias="hub.mode"),
    hub_token: str = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str = Query(default=None, alias="hub.challenge"),
):
    # print(hub_token)
    # print(hub_mode)
    # print(hub_challenge)
    return int(hub_challenge)
