from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from geo.loader import cargar_base, buscar_partido_desde_ubicacion
from logger_consultas import guardar_consulta
from shapely.geometry import Point

# Lista de tablas de Supabase disponibles
PARTIDOS_DISPONIBLES = ["55", "56", "57"]

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.location:
        return await update.message.reply_text("No se recibió una ubicación válida.")

    lat = update.message.location.latitude
    lon = update.message.location.longitude

    # Buscar partido
    partido = buscar_partido_desde_ubicacion(lat, lon, PARTIDOS_DISPONIBLES)
    if not partido:
        await update.message.reply_text("No se encontró el partido para esta ubicación.")
        return

    # Buscar partida dentro del partido
    gdf = cargar_base(partido)
    punto = Point(lon, lat)
    resultado = gdf[gdf.geometry.contains(punto)]
    
    if resultado.empty:
        await update.message.reply_text("No se encontró la partida dentro del partido.")
        return

    # Guardar la consulta
    try:
        mensaje_log = f"Ubicación recibida: Lat: {lat}, Lon: {lon}, Partido: {partido}, Partida: {resultado.iloc[0]['PARTIDA']}"
        guardar_consulta(update, tipo="ubicación", mensaje=mensaje_log)
    except Exception as e:
        print(f"Error al guardar en el log: {e}")

    # Enviar resultado al usuario
    result_text = "Resultado encontrado:\n"
    for _, row in resultado.iterrows():
        result_text += (
            f"🔹 Partido: {row.get('PARTIDO', 'N/A')}\n"
            f"🔹 Partida: {row.get('PARTIDA', 'N/A')}\n"
            f"🔹 Superficie: {row.get('sup', 'N/A')} m²\n"
            f"🔹 FOS: {row.get('fos', 'N/A')}\n"
            f"🔹 FOT: {row.get('fota', 'N/A')}\n"
            f"🔹 Densidad: {row.get('dena', 'N/A')}\n"
            "-----------------------\n"
        )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Ver resumen", callback_data="ver_informe_simple")]])
    await update.message.reply_text(result_text, reply_markup=keyboard)
