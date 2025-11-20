import json
import os
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

def start_handler():
    teclado = {
        "keyboard": [
            [{"text": "📍 Compartir ubicación", "request_location": True}],
            [{"text": "🏘️ Buscar por partido y partida"}],
            [{"text": "ℹ️ Ayuda"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

    texto = (
        "👋 ¡Hola! Soy tu *Bot de Indicadores Urbanos* 🏙️\n\n"
        "Podés usar una de las siguientes opciones:\n"
        "📍 Compartí tu ubicación para ver los indicadores del lugar.\n"
        "🏘️ Buscá manualmente por partido y partida.\n"
        "ℹ️ Pedí ayuda para saber más comandos disponibles.\n\n"
        "Elegí una opción del menú 👇"
    )

    return {"text": texto, "reply_markup": json.dumps(teclado)}

def send_message(chat_id, payload):
    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, **payload})

def handler(request, response):
    body = request.get_json()
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if text == "/start":
        send_message(chat_id, start_handler())
    else:
        send_message(chat_id, {"text": "Comando no reconocido"})

    return response.status(200).json({"ok": True})
