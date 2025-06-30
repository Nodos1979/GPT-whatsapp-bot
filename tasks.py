import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from twilio_sender import send_whatsapp_message
import pytz

user_last_reminders = {}

def get_service():
    creds = Credentials.from_authorized_user_info({
        "client_id": os.getenv("GOOGLE_TASKS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_TASKS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_TASKS_REFRESH_TOKEN"),
        "token_uri": "https://oauth2.googleapis.com/token"
    })
    return build("tasks", "v1", credentials=creds)

def get_tasks():
    service = get_service()
    now = datetime.utcnow().isoformat() + "Z"
    results = service.tasks().list(tasklist='@default', showCompleted=False).execute()
    return results.get('items', [])

def send_reminders():
    tasks = get_tasks()
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    for task in tasks:
        title = task.get("title", "")
        due_str = task.get("due")
        task_id = task.get("id")

        if not due_str:
            continue

        due = datetime.fromisoformat(due_str.replace("Z", "+00:00"))
        delta = (now - due).total_seconds()
        key = f"{task_id}"

        if key not in user_last_reminders:
            user_last_reminders[key] = []

        already_sent = user_last_reminders[key]

        if -1801 < (due - now).total_seconds() < -1 and "0" not in already_sent:
            send_whatsapp_message(f"📌 ¡Ya es el momento! ¿Pudiste realizar *{title}*?")
            already_sent.append("0")

        elif -2701 < (due - now).total_seconds() < -1799 and "30" not in already_sent:
            send_whatsapp_message(f"⏳ ¡Hola! Faltan 30 minutos para: *{title}*. ¿Vas bien?")
            already_sent.append("30")

        elif 0 < delta and int(delta) % 900 < 60 and f"r{int(delta)//900}" not in already_sent:
            send_whatsapp_message(f"🔁 Te recuerdo que sigue pendiente *{title}*. ¿Todo bien?")
            already_sent.append(f"r{int(delta)//900}")

def mark_task_complete_by_whatsapp(user):
    service = get_service()
    tasks = get_tasks()
    for task in tasks:
        task_id = task.get("id")
        if task_id in user_last_reminders:
            task["status"] = "completed"
            service.tasks().update(tasklist='@default', task=task_id, body=task).execute()
            del user_last_reminders[task_id]