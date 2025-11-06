from flask import Flask, request, jsonify
import os
import requests

# --- Handlers ---
from handlers.start import start_handler
from handlers.location import handle_location
from handlers.informe_indicadores import enviar_informe_llm

# --- Configuración básica ---
app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Falta la variable BOT_TOKEN")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# --- Función para enviar mensajes a Telegram ---
def send_message(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)


# --- Ruta del webhook ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("📩 Update recibido:", data)

    message = data.get("message", {})
    callback = data.get("callback_query", {})
    chat_id = (
        message.get("chat", {}).get("id")
        or callback.get("message", {}).get("chat", {}).get("id")
    )

    # 🟢 /start
    if "text" in message and message["text"].startswith("/start"):
        resp = start_handler()
        send_message(chat_id, resp["text"], reply_markup=resp["reply_markup"])
        return jsonify({"ok": True})

    # 📍 Ubicación compartida
    if "location" in message:
        lat = message["location"]["latitude"]
        lon = message["location"]["longitude"]
        resp = handle_location(lat, lon)
        send_message(chat_id, resp["text"], reply_markup=resp["reply_markup"])
        return jsonify({"ok": True})

    # 📲 Callback (botones inline)
    if callback:
        data_callback = callback.get("data")
        text_origen = callback.get("message", {}).get("text", "")

        if data_callback == "ver_informe_simple":
            resp = enviar_informe_llm(text_origen)
            send_message(chat_id, resp["text"], reply_markup=resp["reply_markup"])
            return jsonify({"ok": True})

    # ❌ No se reconoció la acción
    return jsonify({"ok": False, "msg": "Sin acción reconocida"})


# --- Endpoint simple para ver que está vivo ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "Bot de Indicadores Urbanos activo"})


# --- Inicialización ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
