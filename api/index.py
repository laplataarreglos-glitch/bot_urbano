import os
import json
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
    try:
        # 1) Cargar JSON del cuerpo correctamente para Vercel
        body_raw = request.body
        data = json.loads(body_raw)

        # 2) Extraer mensaje seguro
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")

        # Si no hay chat_id NO intentes responder
        if not chat_id:
            return response.status(200).json({"ok": True})

        # Comando /start
        if text == "/start":
            send_message(chat_id, start_handler())
        else:
            send_message(chat_id, {"text": "Comando no reconocido"})

        return response.status(200).json({"ok": True})

    except Exception as e:
        # Log para ver el error en Vercel
        print("Error interno:", e)
        return response.status(500).json({"error": str(e)})
