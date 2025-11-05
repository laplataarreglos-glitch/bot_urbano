from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra mensaje de bienvenida con menú principal"""
    if not update.message:
        return

    teclado = [
        [KeyboardButton("📍 Compartir ubicación", request_location=True)],
        [KeyboardButton("🏘️ Buscar por partido y partida")],
        [KeyboardButton("ℹ️ Ayuda")]
    ]

    reply_markup = ReplyKeyboardMarkup(
        teclado,
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await update.message.reply_text(
        "👋 ¡Hola! Soy tu *Bot de Indicadores Urbanos* 🏙️\n\n"
        "Podés usar una de las siguientes opciones:\n"
        "📍 Compartí tu ubicación para ver los indicadores del lugar.\n"
        "🏘️ Buscá manualmente por partido y partida.\n"
        "ℹ️ Pedí ayuda para saber más comandos disponibles.\n\n"
        "Elegí una opción del menú 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
