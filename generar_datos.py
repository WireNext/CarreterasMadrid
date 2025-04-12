import requests
import xml.etree.ElementTree as ET
import json
from pyproj import Transformer

# Descargar el XML
URL = "https://datos.madrid.es/egob/catalogo/202087-0-trafico-intensidad.xml"
response = requests.get(URL)
response.encoding = 'utf-8-sig'
root = ET.fromstring(response.text)

# Transformador de coordenadas
transformer = Transformer.from_crs("EPSG:25830", "EPSG:4326", always_xy=True)

# Colores según nivel de servicio
colores = {
    "0": "#00FF00",  # Verde
    "1": "#FFFF00",  # Amarillo
    "2": "#FF0000",  # Rojo
    "3": "#000000"   # Negro / Cortado
}

geojson = {
    "type": "FeatureCollection",
    "features": []
}

# Ajustes de desplazamiento para dibujar líneas
offset = 0.001  # Grados aprox (ajustable)

for punto in root.findall("pm"):
    id = punto.findtext("idelem")
    descripcion = punto.findtext("descripcion", "Sin descripción")
    intensidad = punto.findtext("intensidad", "0")
    nivel = punto.findtext("nivelServicio", "0")
    x_str = punto.findtext("st_x", "0").replace(",", ".")
    y_str = punto.findtext("st_y", "0").replace(",", ".")

    try:
        x = float(x_str)
        y = float(y_str)
        lon, lat = transformer.transform(x, y)
    except ValueError:
        continue

    # Determinar dirección
    if "E-O" in descripcion:
        coords = [[lon + offset, lat], [lon - offset, lat]]
    elif "O-E" in descripcion:
        coords = [[lon - offset, lat], [lon + offset, lat]]
    elif "N-S" in descripcion:
        coords = [[lon, lat + offset], [lon, lat - offset]]
    elif "S-N" in descripcion:
        coords = [[lon, lat - offset], [lon, lat + offset]]
    else:
        # Dirección desconocida: línea diagonal para que se vea
        coords = [[lon - offset, lat - offset], [lon + offset, lat + offset]]

    feature = {
        "type": "Feature",
        "properties": {
            "id": id,
            "descripcion": descripcion,
            "intensidad": intensidad,
            "nivelServicio": nivel,
            "_umap_options": {
                "color": colores.get(nivel, "#888888"),
                "weight": 5
            }
        },
        "geometry": {
            "type": "LineString",
            "coordinates": coords
        }
    }

    geojson["features"].append(feature)

# Guardar a archivo
with open('madrid_trafico.geojson', 'w') as f:
    json.dump(geojson, f, indent=2)

print("GeoJSON generado correctamente con líneas.")
