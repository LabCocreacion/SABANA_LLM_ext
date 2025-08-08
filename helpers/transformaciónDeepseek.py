import json
import csv

# Definir los nombres de las columnas en el orden correcto
column_names = [
    "nodulos", "morfologia_nodulos", "margenes_nodulos", "densidad_nodulo",
    "microcalcificaciones", "calcificaciones_benignas", "calcificaciones_sospechosas",
    "distribucion_calcificaciones", "presencia_asimetrias", "tipo_asimetria",
    "hallazgos_asociados", "lateralidad_hallazgo", "birads"
]

# Cargar el JSON
with open("structured_data.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Procesar los datos
rows = []
for entry in data:
    row_data = {}
    raw_output = entry["raw_output"]
    
    # Convertir raw_output en clave-valor
    for item in raw_output.split(", "):
        key, value = item.split("=")
        row_data[key.strip()] = value.strip() if value != "NULL" else ""  # Manejo de valores vacíos
    
    # Corrección de nombres incorrectos
    if "marges_nodulos" in row_data:
        row_data["margenes_nodulos"] = row_data.pop("marges_nodulos")  # Corregir clave mal escrita

    # Asegurar que todas las columnas existen en cada fila
    complete_row = {col: row_data.get(col, "") for col in column_names}
    rows.append(complete_row)

# Guardar en CSV con ";" como delimitador
csv_filename = "output.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=column_names, delimiter=";")
    writer.writeheader()
    writer.writerows(rows)

print(f"Archivo CSV '{csv_filename}' generado correctamente con ';' como delimitador.")