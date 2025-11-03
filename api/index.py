import os
import json
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, MessageHandler, filters
from handlers import start, location, informe
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# --- Token del bot desde variables de entorno ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# --- Crear la aplicación del bot ---
bot_app = Application.builder().token(TOKEN).build()

# --- Agregar handlers ---
bot_app.add_handler(MessageHandler(filters.Regex(r"^/start$"), start.start))
bot_app.add_handler(MessageHandler(filters.LOCATION, location.handle_location))
bot_app.add_handler(CallbackQueryHandler(informe.enviar_informe_llm, pattern="ver_informe_simple"))

# --- Crear app ASGI para Vercel ---
app = FastAPI()

@app.get("/")
async def root():
    return JSONResponse({"status": "Bot urbano activo ✅"})

@app.post("/api")
async def telegram_webhook(request: Request):
    try:
        body = await request.body()
        data = json.loads(body)

        update = Update.de_json(data, bot_app.bot)
        await bot_app.process_update(update)

        # Telegram necesita OK como JSON
        return JSONResponse({"ok": True})

    except Exception as e:
        print("⚠️ Error procesando update:", e)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
