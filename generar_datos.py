import requests
import xml.etree.ElementTree as ET
import json

url = "https://datos.madrid.es/egob/catalogo/202087-0-trafico-intensidad.xml"
response = requests.get(url)
response.encoding = 'utf-8'

print("Contenido completo del XML (primeros 2000 caracteres):")
print(response.content[:2000])

root = ET.fromstring(response.content)

# ✅ Estructura base del GeoJSON
geojson = {
    "type": "FeatureCollection",
    "features": []
}

print("\nImprimiendo todos los elementos 'pm':")
for i, pm in enumerate(root.findall(".//pm")):
    idelem = pm.findtext('idelem')
    descripcion = pm.findtext('descripcion')
    intensidad = pm.findtext('intensidad')
    nivelServicio = pm.findtext('nivelServicio')
    st_x = pm.findtext('st_x')
    st_y = pm.findtext('st_y')

    print(f"\nPunto {i + 1}:")
    print(f"idelem: {idelem}, descripcion: {descripcion}, intensidad: {intensidad}, nivelServicio: {nivelServicio}, st_x: {st_x}, st_y: {st_y}")

    if not st_x or not st_y:
        print(f"Faltan coordenadas para idelem: {idelem}")
        continue

    try:
        lon, lat = map(float, st_x.replace(",", ".").strip()), float(st_y.replace(",", ".").strip())
    except ValueError:
        print(f"Error al convertir coordenadas para idelem: {idelem}")
        continue

    color = {
        "0": "#00FF00",
        "1": "#FFA500",
        "2": "#FF0000",
        "3": "#000000"
    }.get(nivelServicio, "#808080")

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

with open('trafico_madrid_umap.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

print("GeoJSON generado correctamente.")
