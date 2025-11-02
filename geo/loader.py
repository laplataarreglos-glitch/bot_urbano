import os
from supabase import create_client
import geopandas as gpd
from shapely import wkb
from shapely.geometry import Point

# --- Inicializar cliente de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def cargar_base(partido: str):
    """
    Carga todos los registros de un partido desde la tabla de Supabase.
    Convierte la geometría a GeoDataFrame.
    """
    partido = str(partido)
    res = supabase.table(partido).select("*").execute()
    data = res.data
    if not data:
        return gpd.GeoDataFrame()
    
    geometries = []
    for row in data:
        geom_wkb = row.pop("geometry", None)
        geometries.append(wkb.loads(bytes.fromhex(geom_wkb)) if geom_wkb else None)

    gdf = gpd.GeoDataFrame(data, geometry=geometries, crs="EPSG:4326")
    return gdf

def buscar_por_partida(partido: str, partida: int):
    gdf = cargar_base(partido)
    if gdf.empty:
        return None
    resultado = gdf[gdf['PARTIDA'] == int(partida)]
    return resultado if not resultado.empty else None

def buscar_partido_desde_ubicacion(lat: float, lon: float, partido_list: list):
    """
    Itera sobre las tablas de partidos y devuelve el partido que contiene el punto.
    """
    punto = Point(lon, lat)
    
    for partido in partido_list:
        gdf = cargar_base(partido)
        if gdf.empty:
            continue
        if gdf.contains(punto).any():
            return partido
    return None
