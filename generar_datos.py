import requests
import xml.etree.ElementTree as ET
import json

url = "https://datos.madrid.es/egob/catalogo/202087-0-trafico-intensidad.xml"
response = requests.get(url)
response.encoding = 'utf-8'  # Asegurarse de que la respuesta esté bien codificada

# Verificación del contenido del XML (todo el contenido, no solo los primeros 1000 caracteres)
print("Contenido completo del XML (primeros 2000 caracteres):")
print(response.content[:2000])  # Muestra los primeros 2000 caracteres del XML

root = ET.fromstring(response.content)

# Depuración: Imprimir todas las etiquetas "pm" para ver su estructura
print("\nImprimiendo todos los elementos 'pm':")
for i, pm in enumerate(root.findall(".//pm")):
    idelem = pm.findtext('idelem')
    descripcion = pm.findtext('descripcion')
    intensidad = pm.findtext('intensidad')
    nivelServicio = pm.findtext('nivelServicio')
    st_x = pm.findtext('st_x')
    st_y = pm.findtext('st_y')

    # Mostrar todos los campos para comprobar su contenido
    print(f"\nPunto {i + 1}:")
    print(f"idelem: {idelem}, descripcion: {descripcion}, intensidad: {intensidad}, nivelServicio: {nivelServicio}, st_x: {st_x}, st_y: {st_y}")
    
    # Si no hay coordenadas, lo indicamos
    if not st_x or not st_y:
        print(f"Faltan coordenadas para idelem: {idelem}")
        continue

    # Intentamos convertir las coordenadas
    try:
        lon, lat = map(float, st_x.split(','))
    except ValueError:
        print(f"Error al convertir coordenadas para idelem: {idelem}")
        continue

    # Asignamos el color según el nivel de servicio
    color = {
        "0": "#00FF00",  # verde
        "1": "#FFA500",  # naranja
        "2": "#FF0000",  # rojo
        "3": "#000000"   # negro
    }.get(nivelServicio, "#808080")  # gris si no se encuentra el nivel

    # Creamos el feature para el GeoJSON
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
