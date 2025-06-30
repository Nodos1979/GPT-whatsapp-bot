from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from gpt_connector import send_to_gpt
from reminder_scheduler import schedule_reminders
import json
import os

app = Flask(__name__)
DB_PATH = "gpt_whatsapp_bot/db.json"

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    # Enviar mensaje al GPT
    task_data = send_to_gpt(incoming_msg)

    if not task_data:
        resp = MessagingResponse()
        msg = resp.message()
        msg.body("No pude interpretar la tarea. Intenta con un formato diferente.")
        return str(resp)

    task_data["sender"] = sender
    task_data["done"] = False

    # Guardar tarea
    try:
        with open(DB_PATH, "r") as f:
            tasks = json.load(f)
    except:
        tasks = []

    tasks.append(task_data)

    with open(DB_PATH, "w") as f:
        json.dump(tasks, f, indent=2)

    # Programar recordatorios
    schedule_reminders(task_data)

    # Confirmación
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(f"✅ Tarea creada: {task_data['title']} para {task_data['due']}")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)