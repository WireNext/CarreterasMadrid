import requests
import xml.etree.ElementTree as ET
import json
from pyproj import Transformer

URL = "https://datos.madrid.es/egob/catalogo/202087-0-trafico-intensidad.xml"

response = requests.get(URL)
response.encoding = 'utf-8-sig'
root = ET.fromstring(response.text)

transformer = Transformer.from_crs("EPSG:25830", "EPSG:4326", always_xy=True)

colores = {
    "0": "#00FF00",  # Verde
    "1": "#FFA500",  # Naranja
    "2": "#FF0000",  # Rojo
    "3": "#000000"   # Cortado / Negro
}

geojson = {
    "type": "FeatureCollection",
    "features": []
}

# Tamaño del segmento
offset_x = 0.0003
offset_y = 0.0001

for punto in root.findall("pm"):
    id = punto.findtext("idelem")
    descripcion = punto.findtext("descripcion")
    intensidad = punto.findtext("intensidad")
    nivel = punto.findtext("nivelServicio", "0")
    x_str = punto.findtext("st_x", "0").replace(",", ".")
    y_str = punto.findtext("st_y", "0").replace(",", ".")

    try:
        x = float(x_str)
        y = float(y_str)
        lon, lat = transformer.transform(x, y)
    except ValueError:
        continue

    # Determinar el sentido desde la descripción
    if "E-O" in descripcion:
        coords = [[lon + offset_x, lat], [lon - offset_x, lat]]
    elif "O-E" in descripcion:
        coords = [[lon - offset_x, lat], [lon + offset_x, lat]]
    elif "N-S" in descripcion:
        coords = [[lon, lat + offset_y], [lon, lat - offset_y]]
    elif "S-N" in descripcion:
        coords = [[lon, lat - offset_y], [lon, lat + offset_y]]
    else:
        # Si no se puede detectar el sentido, hacer una pequeña línea diagonal
        coords = [[lon - offset_x, lat - offset_y], [lon + offset_x, lat + offset_y]]

    feature = {
        "type": "Feature",
        "properties": {
            "id": id,
            "descripcion": descripcion,
            "intensidad": intensidad,
            "nivelServicio": nivel,
            "_umap_options": {
                "color": colores.get(nivel, "#888888"),
                "weight": 5  # grosor de línea
            }
        },
        "geometry": {
            "type": "LineString",
            "coordinates": coords
        }
    }

    geojson["features"].append(feature)

# Guardar el archivo
with open('madrid_trafico.geojson', 'w') as f:
    json.dump(geojson, f, indent=2)

print("GeoJSON generado correctamente.")
