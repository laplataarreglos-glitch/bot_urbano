from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    teclado = [
        [KeyboardButton("Compartir ubicación", request_location=True)]
    ]

    reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)

    await update.message.reply_text(
        "👋 ¡Hola! Soy un bot de consulta catastral.\n\n"
        "📍 Podés compartirme tu ubicación para buscar información territorial.",
        reply_markup=reply_markup
    )
