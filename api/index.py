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

# --- Envío seguro de mensajes ---
def send_message(chat_id, resp):
    """Envía un mensaje a Telegram validando los campos"""
    if not chat_id:
        logging.warning("⚠️ chat_id ausente en send_message()")
        return

    if not resp or not isinstance(resp, dict):
        logging.warning(f"⚠️ Respuesta inválida: {resp}")
        return

    text = resp.get("text")
    if not text:
        logging.warning("⚠️ Mensaje sin texto, no se envía nada.")
        return

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }

    reply_markup = resp.get("reply_markup")
    if reply_markup:
        try:
            payload["reply_markup"] = json.dumps(reply_markup)
        except Exception as e:
            logging.error(f"Error serializando reply_markup: {e}")

    try:
        res = requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=10)
        if not res.ok:
            logging.error(f"❌ Error al enviar mensaje: {res.status_code} - {res.text}")
    except Exception as e:
        logging.error(f"❌ Exception enviando mensaje: {e}")

# --- Webhook principal ---
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update = request.get_json(silent=True) or {}
        logging.info(f"📩 Update recibido: {json.dumps(update, ensure_ascii=False)}")

        message = update.get("message", {})
        callback = update.get("callback_query", {})
        chat_id = (
            message.get("chat", {}).get("id")
            or callback.get("message", {}).get("chat", {}).get("id")
        )

        if not chat_id:
            logging.warning("⚠️ No se encontró chat_id en el update")
            return jsonify({"ok": False, "msg": "Sin chat_id"})

        # 🟢 /start
        if "text" in message and message["text"].startswith("/start"):
            resp = start_handler()
            send_message(chat_id, resp)
            return jsonify({"ok": True})

        # 📍 Ubicación compartida
        if "location" in message:
            lat = message["location"].get("latitude")
            lon = message["location"].get("longitude")
            if lat and lon:
                resp = handle_location(lat, lon)
                send_message(chat_id, resp)
            else:
                send_message(chat_id, {"text": "❌ Coordenadas inválidas."})
            return jsonify({"ok": True})

        # 📲 Callback de botones inline
        if callback:
            data_callback = callback.get("data")
            text_origen = callback.get("message", {}).get("text", "")

            if data_callback == "ver_informe_simple":
                resp = enviar_informe_llm(text_origen)
                send_message(chat_id, resp)
                return jsonify({"ok": True})

            elif data_callback == "volver_resultado":
                send_message(chat_id, {"text": "🔙 Volviendo al resultado anterior."})
                return jsonify({"ok": True})

            else:
                logging.info(f"⚠️ Callback no reconocido: {data_callback}")
                send_message(chat_id, {"text": "⚠️ Opción no reconocida."})
                return jsonify({"ok": True})

        logging.info("⚙️ Update sin acción reconocida.")
        return jsonify({"ok": True})

    except Exception as e:
        logging.error(f"💥 Error en webhook: {e}", exc_info=True)
        # Devolvemos siempre un JSON válido para evitar error 500
        return jsonify({"ok": False, "error": str(e)}), 200

# --- Endpoint de test ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "msg": "Bot de Indicadores Urbanos activo"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
