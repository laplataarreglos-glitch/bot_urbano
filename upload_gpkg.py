import os
import geopandas as gpd
from supabase import create_client, Client


# --- Configuración Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")  # clave secreta de servicio
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# --- Carpeta donde están los archivos ---
DATA_FOLDER = r"C:\00_bots\bot_test\data"

# --- Subida de cada archivo ---
for file in os.listdir(DATA_FOLDER):
    if file.endswith(".gpkg"):
        path = os.path.join(DATA_FOLDER, file)
        layer_name = os.path.splitext(file)[0]
        print(f"📂 Subiendo {layer_name}...")

        # Cargar con geopandas
        gdf = gpd.read_file(path)

        # Convertir geometría a GeoJSON (WGS84)
        gdf = gdf.to_crs(4326)
        gdf["geometry"] = gdf["geometry"].apply(lambda g: g.__geo_interface__)

        # Convertir a dicts para Supabase
        data = gdf.to_dict(orient="records")

        # Crear tabla si no existe
        try:
            supabase.table(layer_name).select("*").limit(1).execute()
        except Exception:
            print(f"⚙️ Creando tabla {layer_name}...")
            # Crear tabla vacía (sin geometría real, Supabase no soporta crear tablas vía API)
            # Así que primero subimos los datos
            pass

        # Subir registros
        chunk_size = 100
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            supabase.table(layer_name).insert(chunk).execute()

        print(f"✅ {layer_name} subido correctamente.")
