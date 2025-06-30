import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
GPT_ID = os.getenv("GPT_ID")

def send_to_gpt(user_input):
    try:
        response = openai.ChatCompletion.create(
            model=GPT_ID,
            messages=[
                {"role": "user", "content": user_input}
            ]
        )
        function_call = response.choices[0].message.get("function_call")
        if function_call:
            arguments = eval(function_call["arguments"])
            return arguments
        return None
    except Exception as e:
        print(f"Error al enviar a GPT: {e}")
        return None