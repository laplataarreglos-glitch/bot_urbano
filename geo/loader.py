import os
from upload_gpkg import create_client
from typing import Optional, Dict

# --- Inicializar cliente de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def buscar_partido_desde_ubicacion(lat: float, lon: float, partidos: list) -> Optional[str]:
    """
    Busca el partido que contiene el punto (lat, lon) usando PostGIS directamente en Supabase.
    """
    for partido in partidos:
        sql = f"""
        SELECT 1
        FROM {partido}
        WHERE ST_Contains(geometry, ST_SetSRID(ST_Point({lon}, {lat}), 4326))
        LIMIT 1;
        """
        try:
            res = supabase.rpc("exec_sql", {"sql": sql}).execute()
            if res.data:
                return partido
        except Exception as e:
            print(f"Error buscando en partido {partido}: {e}")
    return None


async def buscar_por_partida(partido: str, partida: int) -> Optional[Dict]:
    """
    Devuelve una fila con los atributos de la partida indicada.
    """
    try:
        res = supabase.table(partido).select("*").eq("PARTIDA", partida).limit(1).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        print(f"Error al buscar partida {partida} en {partido}: {e}")
    return None


async def buscar_por_ubicacion(partido: str, lat: float, lon: float) -> Optional[Dict]:
    """
    Devuelve la parcela que contiene el punto, sin cargar geometrías completas.
    """
    sql = f"""
    SELECT PARTIDO, PARTIDA, sup, fos, fota, dena
    FROM {partido}
    WHERE ST_Contains(geometry, ST_SetSRID(ST_Point({lon}, {lat}), 4326))
    LIMIT 1;
    """
    try:
        res = supabase.rpc("exec_sql", {"sql": sql}).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        print(f"Error al buscar por ubicación en {partido}: {e}")
    return None
