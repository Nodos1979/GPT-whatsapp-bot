import openai
import os
import json

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
GPT_ID = os.getenv("GPT_ID")

def send_to_gpt(user_input):
    try:
        response = client.chat.completions.create(
            model=GPT_ID,
            messages=[
                {"role": "user", "content": user_input}
            ],
            functions=[
                {
                    "name": "create_google_task",
                    "description": "Crea una tarea en Google Tasks con título, fecha, hora y notas opcionales.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Título o nombre claro de la tarea."
                            },
                            "due": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Fecha y hora de vencimiento en formato ISO 8601."
                            },
                            "notes": {
                                "type": "string",
                                "description": "Notas o ubicación relacionada con la tarea (opcional)."
                            }
                        },
                        "required": ["title", "due"]
                    }
                }
            ],
            function_call={"name": "create_google_task"}
        )

        fn_call = response.choices[0].message.function_call
        if fn_call and fn_call.name == "create_google_task":
            args = json.loads(fn_call.arguments)
            return args
        return None
    except Exception as e:
        print(f"Error al enviar a GPT: {e}")
        return None