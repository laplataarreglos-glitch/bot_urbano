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
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Falta la variable BOT_TOKEN")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# --- Función para enviar mensajes a Telegram ---
def send_message(chat_id, resp):
    """Envía un mensaje validando 'text' y 'reply_markup'."""
    if not chat_id or not resp or not isinstance(resp, dict):
        logging.warning(f"⚠️ Datos inválidos: chat_id={chat_id}, resp={resp}")
        return

    text = resp.get("text")
    reply_markup = resp.get("reply_markup")

    if not text:
        logging.warning(f"⚠️ No hay 'text' en resp: {resp}")
        return

    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        try:
            payload["reply_markup"] = json.dumps(reply_markup)
        except Exception as e:
            logging.error(f"Error serializando reply_markup: {e}")

    try:
        res = requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=10)
        if not res.ok:
            logging.error(f"❌ Error al enviar mensaje: {res.text}")
    except Exception as e:
        logging.error(f"❌ Exception enviando mensaje: {e}")

# --- Webhook principal ---
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # Soporte GET (para evitar 404 en test de Telegram)
    if request.method == "GET":
        return jsonify({"ok": True, "msg": "Webhook activo"})

    # Procesamiento del POST (mensajes reales)
    update = request.get_json(silent=True) or {}
    logging.info(f"📩 Update recibido: {update}")

    message = update.get("message", {})
    callback = update.get("callback_query", {})
    chat_id = (
        message.get("chat", {}).get("id")
        or callback.get("message", {}).get("chat", {}).get("id")
    )

    if not chat_id:
        logging.warning("⚠️ Update sin chat_id")
        return jsonify({"ok": False, "msg": "Sin chat_id"})

    # 🟢 /start
    if "text" in message and message["text"].startswith("/start"):
        logging.info("🟢 Comando /start recibido")
        resp = start_handler()
        send_message(chat_id, resp)
        return jsonify({"ok": True})

    # 📍 Ubicación compartida
    if "location" in message:
        lat = message["location"]["latitude"]
        lon = message["location"]["longitude"]
        logging.info(f"📍 Ubicación recibida: lat={lat}, lon={lon}")
        resp = handle_location(lat, lon)
        send_message(chat_id, resp)
        return jsonify({"ok": True})

    # 📲 Callback (botones inline)
    if callback:
        data_callback = callback.get("data")
        text_origen = callback.get("message", {}).get("text", "")
        logging.info(f"🔘 Callback recibido: {data_callback}")

        if data_callback == "ver_informe_simple":
            resp = enviar_informe_llm(text_origen)
            send_message(chat_id, resp)
            return jsonify({"ok": True})
        else:
            logging.info(f"⚠️ Callback no reconocido: {data_callback}")
            return jsonify({"ok": False, "msg": "Callback no reconocido"})

    # Si no se reconoce acción
    logging.info("⚠️ Ninguna acción reconocida")
    return jsonify({"ok": False, "msg": "Sin acción reconocida"})

# --- Endpoint de estado ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "msg": "Bot de Indicadores Urbanos activo"})

# --- Main ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
