from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from supabase import create_client
import os

# --- Configuración de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Lista de tablas disponibles
PARTIDOS_DISPONIBLES = ["55", "56", "57"]

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.location:
        return await update.message.reply_text("⚠️ No se recibió una ubicación válida.")

    lat = update.message.location.latitude
    lon = update.message.location.longitude

    partido = await buscar_partido_desde_ubicacion(lat, lon)
    if not partido:
        return await update.message.reply_text("🚫 No se encontró el partido para esta ubicación.")

    resultado = await buscar_partida_por_ubicacion(partido, lat, lon)
    if not resultado:
        return await update.message.reply_text("🔍 No se encontró la partida dentro del partido.")

    row = resultado[0]
    result_text = (
        "📍 *Resultado encontrado:*\n\n"
        f"🏙️ Partido: {row.get('partido', 'N/A')}\n"
        f"🏠 Partida: {row.get('partida', 'N/A')}\n"
        f"📐 Superficie: {row.get('sup', 'N/A')} m²\n"
        f"🏗️ FOS: {row.get('fos', 'N/A')}\n"
        f"🏢 FOT: {row.get('fota', 'N/A')}\n"
        f"👥 Densidad: {row.get('dena', 'N/A')}\n"
    )

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📊 Ver resumen", callback_data="ver_informe_simple")]]
    )
    await update.message.reply_text(result_text, parse_mode="Markdown", reply_markup=keyboard)

# --- FUNCIONES AUXILIARES ---

async def buscar_partido_desde_ubicacion(lat, lon):
    """
    Itera por los partidos disponibles y devuelve el primero que contenga el punto.
    Usa la función ST_Contains desde Supabase.
    """
    for partido in PARTIDOS_DISPONIBLES:
        sql = f"""
        select 1 from {partido}
        where ST_Contains(geometry, ST_SetSRID(ST_Point({lon}, {lat}), 4326))
        limit 1;
        """
        res = supabase.rpc("exec_sql", {"sql": sql}).execute()
        if res.data and len(res.data) > 0:
            return partido
    return None

async def buscar_partida_por_ubicacion(partido, lat, lon):
    """
    Busca los datos completos de la partida que contiene el punto.
    """
    sql = f"""
    select * from {partido}
    where ST_Contains(geometry, ST_SetSRID(ST_Point({lon}, {lat}), 4326))
    limit 1;
    """
    res = supabase.rpc("exec_sql", {"sql": sql}).execute()
    if res.data and len(res.data) > 0:
        return res.data
    return None
