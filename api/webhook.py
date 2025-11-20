import json
import os
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE = f"https://api.telegram.org/bot{TOKEN}"

def send(chat_id, payload):
    requests.post(f"{BASE}/sendMessage", json={"chat_id": chat_id, **payload})

def handler(request, response):
    try:
        body = json.loads(request.body)
        msg = body.get("message", {})
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text")

        if not chat_id:
            return response.status(200).json({"ok": True})

        if text == "/start":
            send(chat_id, {"text": "Bot funcionando en Vercel ✓"})
        else:
            send(chat_id, {"text": "Comando no reconocido"})

        return response.status(200).json({"ok": True})

    except Exception as e:
        print("Error:", e)
        return response.status(500).json({"error": str(e)})
