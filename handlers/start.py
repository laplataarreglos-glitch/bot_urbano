import json

def start_handler():
    """Devuelve el mensaje y teclado de inicio del bot"""

    teclado = {
        "keyboard": [
            [{"text": "📍 Compartir ubicación", "request_location": True}],
            [{"text": "🏘️ Buscar por partido y partida"}],
            [{"text": "ℹ️ Ayuda"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

    texto = (
        "👋 ¡Hola! Soy tu *Bot de Indicadores Urbanos* 🏙️\n\n"
        "Podés usar una de las siguientes opciones:\n"
        "📍 Compartí tu ubicación para ver los indicadores del lugar.\n"
        "🏘️ Buscá manualmente por partido y partida.\n"
        "ℹ️ Pedí ayuda para saber más comandos disponibles.\n\n"
        "Elegí una opción del menú 👇"
    )

    # Telegram necesita que el reply_markup se envíe como JSON
    return {"text": texto, "reply_markup": json.dumps(teclado)}
