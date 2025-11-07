import os
from supabase import create_client
import logging

# --- Configuración de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Faltan las variables SUPABASE_URL o SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

PARTIDOS_DISPONIBLES = ["55", "56", "57"]

# --- Función principal ---
def handle_location(lat: float, lon: float):
    """Busca el partido y partida y devuelve texto + botones seguros."""
    try:
        partido = buscar_partido_desde_ubicacion(lat, lon)
        if not partido:
            return {"text": "🚫 No se encontró el partido para esta ubicación.", "reply_markup": {}}

        resultado = buscar_partida_por_ubicacion(partido, lat, lon)
        if not resultado or len(resultado) == 0:
            return {"text": "🔍 No se encontró la partida dentro del partido.", "reply_markup": {}}

        row = resultado[0]
        # aseguramos que todos los campos existan
        sup_val = row.get('sup', 'N/A')
        fos_val = row.get('fos', 'N/A')
        fota_val = row.get('fota', 'N/A')
        dena_val = row.get('dena', 'N/A')
        partido_val = row.get('partido', 'N/A')
        partida_val = row.get('partida', 'N/A')

        result_text = (
            "📍 *Resultado encontrado:*\n\n"
            f"🏙️ Partido: {partido_val}\n"
            f"🏠 Partida: {partida_val}\n"
            f"📐 Superficie: {sup_val} m²\n"
            f"🏗️ FOS: {fos_val}\n"
            f"🏢 FOT: {fota_val}\n"
            f"👥 Densidad: {dena_val}\n"
        )

        keyboard = {"inline_keyboard": [[{"text": "📊 Ver resumen", "callback_data": "ver_informe_simple"}]]}

        return {"text": result_text, "reply_markup": keyboard}

    except Exception as e:
        logging.error(f"⚠️ Error en handle_location: {e}")
        return {"text": "❌ Ocurrió un error al procesar la ubicación.", "reply_markup": {}}


# --- Funciones auxiliares ---
def buscar_partido_desde_ubicacion(lat, lon):
    try:
        for partido in PARTIDOS_DISPONIBLES:
            sql = f"""
            SELECT 1 FROM {partido}
            WHERE ST_Contains(geometry, ST_SetSRID(ST_Point({lon}, {lat}), 4326))
            LIMIT 1;
            """
            res = supabase.rpc("exec_sql", {"sql": sql}).execute()
            if res.data and len(res.data) > 0:
                return partido
    except Exception as e:
        logging.error(f"Error buscando en partido {partido}: {e}")
    return None


def buscar_partida_por_ubicacion(partido, lat, lon):
    try:
        sql = f"""
        SELECT * FROM {partido}
        WHERE ST_Contains(geometry, ST_SetSRID(ST_Point({lon}, {lat}), 4326))
        LIMIT 1;
        """
        res = supabase.rpc("exec_sql", {"sql": sql}).execute()
        if res.data and len(res.data) > 0:
            return res.data
    except Exception as e:
        logging.error(f"Error al buscar partida por ubicación en {partido}: {e}")
    return None
