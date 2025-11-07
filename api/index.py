import os
import json
import logging
import requests
from flask import Flask, request, jsonify

# --- Handlers ---
from handlers.start import start_handler
from handlers.location import handle_location
from handlers.informe_indicadores import enviar_informe_llm

# --- Configuración básica ---
app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Falta la variable BOT_TOKEN")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# --- Función para enviar mensajes a Telegram ---
def send_message(chat_id, resp):
    """Envía un mensaje seguro, validando que resp tenga 'text' y 'reply_markup'"""
    if not chat_id:
        logging.warning("⚠️ chat_id es None, no se puede enviar mensaje")
        return
    if not resp or not isinstance(resp, dict):
        logging.warning(f"⚠️ resp inválido: {resp}")
        return

    text = resp.get("text")
    reply_markup = resp.get("reply_markup")

    if not text:
        logging.warning(f"⚠️ No hay 'text' en resp: {resp}")
        return

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }

    if reply_markup:
        # Telegram no acepta None dentro del reply_markup
        try:
            payload["reply_markup"] = json.dumps(reply_markup)
        except Exception as e:
            logging.error(f"Error serializando reply_markup: {e}")
            payload.pop("reply_markup", None)

    try:
        res = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload, timeout=10)
        if not res.ok:
            logging.error(f"❌ Error al enviar mensaje: {res.text}")
    except Exception as e:
        logging.error(f"❌ Exception en safe_send_message: {e}")


# --- Ruta del webhook ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    logging.info(f"📩 Update recibido: {data}")

    message = data.get("message", {})
    callback = data.get("callback_query", {})
    chat_id = (
        message.get("chat", {}).get("id")
        or callback.get("message", {}).get("chat", {}).get("id")
    )

    if not chat_id:
        return jsonify({"ok": False, "msg": "Sin chat_id"})

    # 🟢 /start
    if "text" in message and message["text"].startswith("/start"):
        resp = start_handler()
        send_message(chat_id, resp)   # <- reemplaza send_message
        return jsonify({"ok": True})

    # 📍 Ubicación compartida
    if "location" in message:
        lat = message["location"]["latitude"]
        lon = message["location"]["longitude"]
        resp = handle_location(lat, lon)
        safe_send_message(chat_id, resp)   # <- reemplaza send_message
        return jsonify({"ok": True})

    # 📲 Callback (botones inline)
    if callback:
        data_callback = callback.get("data")
        text_origen = callback.get("message", {}).get("text", "")

        if data_callback == "ver_informe_simple":
            resp = enviar_informe_llm(text_origen)
            send_message(chat_id, resp)  # <- reemplaza send_message
            return jsonify({"ok": True})
        else:
            logging.info(f"⚠️ Callback no reconocido: {data_callback}")

    return jsonify({"ok": False, "msg": "Sin acción reconocida"})

# --- Endpoint simple para ver que está vivo ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "Bot de Indicadores Urbanos activo"})


# --- Inicialización ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# Requerido por Vercel
handler = app
