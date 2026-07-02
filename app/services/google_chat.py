import os
import requests
from dotenv import load_dotenv

load_dotenv()


def send_google_chat_message(message: str) -> bool:
    webhook_url = os.getenv("GOOGLE_CHAT_WEBHOOK_URL")

    if not webhook_url:
        print("GOOGLE_CHAT_WEBHOOK_URL não configurado.")
        return False

    response = requests.post(
        webhook_url,
        json={"text": message},
        timeout=30,
    )

    if response.status_code >= 400:
        print("Erro ao enviar Google Chat:", response.status_code, response.text)
        return False

    return True