from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO

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
        "Content-Type": "application/json",
    }

    data = {
        "messaging_product": "whatsapp",
        "to": payload.to,
        "type": "template",
        "template": {"name": "hello_world", "language": {"code": "en_US"}},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(WHATSAPP_API_URL, json=data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=response.text)

    return {"status": "message sent", "response": response.json()}



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
    return {'res':results}
