import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Falta la variable BOT_TOKEN")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    payload = {"chat_id": chat_id, "text": text}
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "msg": "Bot conectado a Telegram"})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")

    if not chat_id:
        return jsonify({"ok": False, "msg": "sin chat_id"})

    if text == "/start":
        send_message(chat_id, "👋 Bot activo en Vercel")
        return jsonify({"ok": True})

    send_message(chat_id, f"Recibí: {text}")
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
