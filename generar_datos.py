import requests
import xml.etree.ElementTree as ET
import json

url = "https://datos.madrid.es/egob/catalogo/202087-0-trafico-intensidad.xml"
response = requests.get(url)
response.encoding = 'utf-8'

root = ET.fromstring(response.text)

features = []

for punto in root.findall('.//pm'):
    idpm = punto.find('idpm')
    lat = punto.find('lat')
    lon = punto.find('lon')
    intensidad = punto.find('intensidad')

    if idpm is None or lat is None or lon is None or intensidad is None:
        continue  # saltar si falta algo

    intensidad_valor = int(intensidad.text)

    # colores según intensidad
    if intensidad_valor < 500:
        color = "#00FF00"  # verde
    elif intensidad_valor < 1500:
        color = "#FFA500"  # naranja
    else:
        color = "#FF0000"  # rojo

    feature = {
        "type": "Feature",
        "properties": {
            "id": idpm.text,
            "intensidad": intensidad_valor,
            "color": color
        },
        "geometry": {
            "type": "Point",
            "coordinates": [float(lon.text), float(lat.text)]
        }
    }
    features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open('madrid_trafico.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)
