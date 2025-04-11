import requests
import xml.etree.ElementTree as ET
import json

URL = 'https://datos.madrid.es/egob/catalogo/202087-0-trafico-intensidad.xml'

def get_color(intensidad):
    intensidad = int(intensidad)
    if intensidad < 500:
        return '#00FF00'
    elif intensidad < 1000:
        return '#FFA500'
    else:
        return '#000000'

response = requests.get(URL)
response.raise_for_status()

root = ET.fromstring(response.content)

features = []

for punto in root.findall('.//pm'):
    id = punto.find('idpm').text
    intensidad = punto.find('intensidad').text or '0'
    nombre = punto.find('nombre').text or 'Sin nombre'
    lat = float(punto.find('lat').text)
    lon = float(punto.find('long').text)

    color = get_color(intensidad)

    feature = {
        "type": "Feature",
        "properties": {
            "id": id,
            "nombre": nombre,
            "intensidad": intensidad,
            "marker-color": color
        },
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat]
        }
    }
    features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open('trafico_madrid_umap.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

print("GeoJSON generado correctamente")
