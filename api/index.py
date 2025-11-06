import os
import requests
from flask import Flask, request, jsonify

# --- Configuración del bot ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ Falta TELEGRAM_TOKEN")

BOT_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# --- Rutas ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Bot urbano activo ✅"}), 200

@app.route("/api", methods=["POST"])
def webhook():
    """Recibe actualizaciones de Telegram"""
    try:
        data = request.get_json(force=True)

        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            # --- Comando /start ---
            if text == "/start":
                return send_welcome(chat_id)

            # --- Si el usuario envía ubicación ---
            if "location" in data["message"]:
                lat = data["message"]["location"]["latitude"]
                lon = data["message"]["location"]["longitude"]
                return send_location_info(chat_id, lat, lon)

            # --- Cualquier otro texto ---
            send_message(chat_id, "ℹ️ Usá /start para comenzar o compartí tu ubicación.")
        return jsonify({"ok": True})
    except Exception as e:
        print("❌ Error en webhook:", e)
        return jsonify({"ok": False, "error": str(e)}), 500


# --- Funciones auxiliares ---
def send_message(chat_id, text, keyboard=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if keyboard:
        payload["reply_markup"] = keyboard
    requests.post(f"{BOT_URL}/sendMessage", json=payload)


def send_welcome(chat_id):
    keyboard = {
        "keyboard": [
            [{"text": "📍 Compartir ubicación", "request_location": True}],
            [{"text": "🏘️ Buscar por partido y partida"}],
            [{"text": "ℹ️ Ayuda"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

    mensaje = (
        "👋 ¡Hola! Soy tu *Bot de Indicadores Urbanos* 🏙️\n\n"
        "Podés usar una de las siguientes opciones:\n"
        "📍 Compartí tu ubicación para ver los indicadores del lugar.\n"
        "🏘️ Buscá manualmente por partido y partida.\n"
        "ℹ️ Pedí ayuda para saber más comandos disponibles.\n\n"
        "Elegí una opción del menú 👇"
    )

    send_message(chat_id, mensaje, keyboard)
    return jsonify({"ok": True})


def send_location_info(chat_id, lat, lon):
    mensaje = f"📍 Recibí tu ubicación: {lat:.5f}, {lon:.5f}\n\nBuscando indicadores..."
    send_message(chat_id, mensaje)
    return jsonify({"ok": True})


# --- Para Vercel ---
handler = app
