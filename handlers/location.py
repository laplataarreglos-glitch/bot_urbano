import os
from supabase import create_client

# --- Configuración de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Faltan las variables SUPABASE_URL o SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Tablas disponibles ---
PARTIDOS_DISPONIBLES = ["55", "56", "57"]


def handle_location(lat: float, lon: float):
    """Busca el partido y partida correspondientes a una ubicación y devuelve texto + botones."""
    partido = buscar_partido_desde_ubicacion(lat, lon)
    if not partido:
        return {
            "text": "🚫 No se encontró el partido para esta ubicación.",
            "reply_markup": None,
        }

    resultado = buscar_partida_por_ubicacion(partido, lat, lon)
    if not resultado:
        return {
            "text": "🔍 No se encontró la partida dentro del partido.",
            "reply_markup": None,
        }

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

    keyboard = {
        "inline_keyboard": [
            [{"text": "📊 Ver resumen", "callback_data": "ver_informe_simple"}]
        ]
    }

    return {"text": result_text, "reply_markup": keyboard}


# --- Funciones auxiliares ---
def buscar_partido_desde_ubicacion(lat, lon):
    for partido in PARTIDOS_DISPONIBLES:
        sql = f"""
        SELECT 1 FROM {partido}
        WHERE ST_Contains(geometry, ST_SetSRID(ST_Point({lon}, {lat}), 4326))
        LIMIT 1;
        """
        try:
            res = supabase.rpc("exec_sql", {"sql": sql}).execute()
            if res.data and len(res.data) > 0:
                return partido
        except Exception as e:
            print(f"Error buscando en partido {partido}: {e}")
    return None


def buscar_partida_por_ubicacion(partido, lat, lon):
    sql = f"""
    SELECT * FROM {partido}
    WHERE ST_Contains(geometry, ST_SetSRID(ST_Point({lon}, {lat}), 4326))
    LIMIT 1;
    """
    try:
        res = supabase.rpc("exec_sql", {"sql": sql}).execute()
        if res.data and len(res.data) > 0:
            return res.data
    except Exception as e:
        print(f"Error al buscar partida por ubicación en {partido}: {e}")
    return None
