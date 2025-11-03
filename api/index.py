import os
import json
from telegram import Update
from telegram.ext import Application, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from handlers import start, location, informe

# --- Token del bot desde variables de entorno ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# --- Crear la aplicación del bot ---
bot_app = Application.builder().token(TOKEN).build()

# --- Agregar handlers ---
# /start
bot_app.add_handler(MessageHandler(filters.Regex(r"^/start$"), start.start))

# Ubicación
bot_app.add_handler(MessageHandler(filters.LOCATION, location.handle_location))

# Callback de "ver resumen"
bot_app.add_handler(CallbackQueryHandler(informe.enviar_informe_llm, pattern="ver_informe_simple"))


# --- Handler principal para Vercel ---
async def handler(request):
    """
    Endpoint principal que recibe las actualizaciones del webhook de Telegram.
    Compatible con FastAPI/ASGI (Vercel lo usa por defecto para Python 3.11+)
    """
    if request.method == "GET":
        return {
            "statusCode": 200,
            "body": "Bot urbano activo ✅"
        }

    if request.method == "POST":
        try:
            # Leer el cuerpo del request
            body = await request.body()
            data = json.loads(body)

            # Procesar update de Telegram
            update = Update.de_json(data, bot_app.bot)
            await bot_app.process_update(update)

            return {"statusCode": 200, "body": "OK"}

        except Exception as e:
            print("⚠️ Error procesando update:", e)
            return {"statusCode": 500, "body": "Error interno del servidor"}
