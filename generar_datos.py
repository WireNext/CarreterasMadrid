import requests
import xml.etree.ElementTree as ET
import json

# URL del XML
url = "https://datos.madrid.es/egob/catalogo/202087-0-trafico-intensidad.xml"

# Obtener el contenido del XML
response = requests.get(url)
xml_data = response.content

# Parsear el XML
root = ET.fromstring(xml_data)

# Inicializar estructura GeoJSON
geojson = {
    "type": "FeatureCollection",
    "features": []
}

# Colores por nivel de servicio
colores = {
    "0": "#00FF00",  # Verde
    "1": "#FFA500",  # Naranja
    "2": "#FF0000",  # Rojo
    "3": "#000000"   # Negro
}

# Procesar cada punto de medida
for i, punto in enumerate(root.findall("pm")):
    try:
        id = punto.find("idelem").text
        descripcion = punto.find("descripcion").text
        intensidad = punto.find("intensidad").text
        nivel = punto.find("nivelServicio").text
        x = punto.find("st_x").text.replace(",", ".")
        y = punto.find("st_y").text.replace(",", ".")

        # Crear Feature
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
                "coordinates": [float(x), float(y)]
            }
        }

        geojson["features"].append(feature)

    except Exception as e:
        print(f"Error procesando el punto {i + 1}: {e}")

# Guardar como GeoJSON
with open("madrid_trafico.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

print("GeoJSON generado correctamente con", len(geojson["features"]), "puntos.")
