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
    "0": "#00FF00",
    "1": "#FFA500",
    "2": "#FF0000",
    "3": "#000000"
}

geojson = {
    "type": "FeatureCollection",
    "features": []
}

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

    feature = {
        "type": "Feature",
        "properties": {
            "id": id,
            "descripcion": descripcion,
            "intensidad": intensidad,
            "nivelServicio": nivel,
            "_umap_options": {
                "color": colores.get(nivel, "#888888")
            }
        },
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat]
        }
    }

    geojson["features"].append(feature)

with open("madrid_trafico.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)
