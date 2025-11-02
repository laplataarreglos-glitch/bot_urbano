import os
import json
from telegram import Update
from telegram.ext import Application, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from handlers import start, location, informe

# --- Token del bot desde variables de entorno ---
TOKEN = os.environ["TELEGRAM_TOKEN"]

# --- Crear la aplicación del bot ---
app = Application.builder().token(TOKEN).build()

# --- Agregar handlers ---
# /start
app.add_handler(MessageHandler(filters.Regex(r"^/start$"), start.start))

# Ubicación
app.add_handler(MessageHandler(filters.LOCATION, location.handle_location))

# Callback de "ver resumen"
app.add_handler(CallbackQueryHandler(informe.enviar_informe_llm, pattern="ver_informe_simple"))

# --- Función principal para Vercel ---
async def handler(request):
    """
    Recibe el POST de Telegram y procesa el update.
    """
    # Telegram manda JSON
    body = await request.body()
    data = json.loads(body)

    update = Update.de_json(data, app.bot)
    await app.update_queue.put(update)
    await app.process_update(update)

    # Respuesta obligatoria para webhook
    return {"statusCode": 200, "body": "OK"}
