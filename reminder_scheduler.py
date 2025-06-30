from apscheduler.schedulers.background import BackgroundScheduler
from twilio.rest import Client
from datetime import datetime, timedelta
import json
import os
import random

DB_PATH = "gpt_whatsapp_bot/db.json"

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

scheduler = BackgroundScheduler()
scheduler.start()

def schedule_reminders(task):
    due = datetime.fromisoformat(task["due"])
    sender = task["sender"]

    scheduler.add_job(lambda: send_reminder(sender, task["title"], "⏰ Recordatorio: faltan 30 minutos."), 'date', run_date=due - timedelta(minutes=30))

    for i in range(1, 10):
        time = due + timedelta(minutes=15 * i)
        scheduler.add_job(lambda: persistent_reminder(sender, task), 'date', run_date=time)

def send_reminder(to, task_title, msg):
    client.messages.create(body=f"{msg} Tarea: {task_title}", from_=twilio_number, to=to)

def persistent_reminder(to, task):
    if not is_pending(task):
        return
    frases = [
        f"🔔 ¿Ya hiciste: {task['title']}?",
        f"📌 Seguimos pendientes con: {task['title']}",
        f"👀 Recordá que aún está pendiente: {task['title']}"
    ]
    client.messages.create(body=random.choice(frases), from_=twilio_number, to=to)

def is_pending(task):
    try:
        with open(DB_PATH, "r") as f:
            tasks = json.load(f)
        for t in tasks:
            if t["title"] == task["title"] and not t["done"]:
                return True
    except:
        return False