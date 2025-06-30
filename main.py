from fastapi import FastAPI, Request, Form
from dotenv import load_dotenv
from tasks import mark_task_complete_by_whatsapp
import os

load_dotenv()
app = FastAPI()

@app.post("/webhook")
async def webhook(From: str = Form(...), Body: str = Form(...)):
    if Body.strip().lower() == "listo":
        mark_task_complete_by_whatsapp(From)
    return "OK"