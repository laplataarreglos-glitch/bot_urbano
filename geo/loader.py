import os
from supabase import create_client
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)

# --- Inicializar cliente de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Faltan variables de entorno SUPABASE_URL o SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def buscar_partido_desde_ubicacion(lat: float, lon: float, partidos: list) -> Optional[str]:
    try:
        for partido in partidos:
            sql = f"""
            SELECT 1
            FROM {partido}
            WHERE ST_Contains(geometry, ST_SetSRID(ST_Point({lon}, {lat}), 4326))
            LIMIT 1;
            """
            res = supabase.rpc("exec_sql", {"sql": sql}).execute()
            if res.data:
                return partido
    except Exception as e:
        logging.error(f"⚠️ Error buscando en partido {partido}: {e}")
    return None

def buscar_por_partida(partido: str, partida: int) -> Optional[Dict]:
    try:
        res = supabase.table(partido).select("*").eq("PARTIDA", partida).limit(1).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        logging.error(f"⚠️ Error al buscar partida {partida} en {partido}: {e}")
    return None

def buscar_por_ubicacion(partido: str, lat: float, lon: float) -> Optional[Dict]:
    try:
        sql = f"""
        SELECT PARTIDO, PARTIDA, sup, fos, fota, dena
        FROM {partido}
        WHERE ST_Contains(geometry, ST_SetSRID(ST_Point({lon}, {lat}), 4326))
        LIMIT 1;
        """
        res = supabase.rpc("exec_sql", {"sql": sql}).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        logging.error(f"⚠️ Error al buscar por ubicación en {partido}: {e}")
    return None
