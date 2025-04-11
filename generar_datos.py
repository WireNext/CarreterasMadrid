import requests
import xml.etree.ElementTree as ET
import json

url = "https://datos.madrid.es/egob/catalogo/202087-0-trafico-intensidad.xml"
response = requests.get(url)
root = ET.fromstring(response.content)

geojson = {
    "type": "FeatureCollection",
    "features": []
}

# Recorremos todos los puntos de tráfico (PM)
for pm in root.findall(".//pm"):
    idelem = pm.findtext('idelem')
    descripcion = pm.findtext('descripcion')
    intensidad = pm.findtext('intensidad')
    nivelServicio = pm.findtext('nivelServicio')
    st_x = pm.findtext('st_x')
    st_y = pm.findtext('st_y')

    # Comprobamos si los campos necesarios están presentes
    if not st_x or not st_y:
        continue

    # Convertimos coordenadas
    try:
        lon, lat = map(float, st_x.split(','))
    except ValueError:
        continue

    # Definimos el color según el nivel de servicio
    color = {
        "0": "#00FF00",  # verde
        "1": "#FFA500",  # naranja
        "2": "#FF0000",  # rojo
        "3": "#000000"   # negro
    }.get(nivelServicio, "#808080")  # gris por defecto si no está en el rango

    feature = {
        "type": "Feature",
        "properties": {
            "id": idelem,
            "descripcion": descripcion,
            "intensidad": intensidad,
            "nivelServicio": nivelServicio,
            "_umap_options": {
                "color": color
            }
        },
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat]
        }
    }
    geojson["features"].append(feature)

# Guardamos el archivo GeoJSON generado
with open('madrid_trafico.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

print("GeoJSON generado correctamente.")
