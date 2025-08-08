import json
import csv
import re

# Función para procesar la cadena raw_output y convertirla a un diccionario
def parse_raw_output(raw_output):
    # Usamos regex para separar cada par clave=valor
    pairs = re.findall(r'(\w+)=([^,]+)(?:,\s*|$)', raw_output)
    
    # Convertir a diccionario
    data = {}
    for key, value in pairs:
        # Convertir "NULL" a cadena vacía
        if value == "NULL":
            data[key] = ""
        else:
            data[key] = value
    
    return data

# Cargar el JSON desde un archivo (o puedes usar un string directamente)
# Aquí suponemos que tienes el JSON en un archivo llamado 'datos.json'
# json_data = json.load(open('datos.json', 'r'))

# Alternativamente, si tienes el JSON como string:
# file is structured_data.json
json_string = 

json_data = json.loads(json_string)

# Lista de campos que queremos incluir en el CSV, en el orden deseado
fields = [
    'nodulos', 'morfologia_nodulos', 'margenes_nodulos', 'densidad_nodulo',
    'microcalcificaciones', 'calcificaciones_benignas', 'calcificaciones_sospechosas',
    'distribucion_calcificaciones', 'presencia_asimetrias', 'tipo_asimetria',
    'hallazgos_asociados', 'lateralidad_hallazgo', 'birads'
]

# Crear archivo CSV
with open('resultado.csv', 'w', newline='') as csvfile:
    # Usar punto y coma como separador
    writer = csv.writer(csvfile, delimiter=';')
    
    # Escribir encabezado
    writer.writerow(fields)
    
    # Procesar cada registro
    for item in json_data:
        data_dict = parse_raw_output(item['raw_output'])
        
        # Crear una fila con los campos en el orden correcto
        row = []
        for field in fields:
            row.append(data_dict.get(field, ""))
        
        # Escribir la fila
        writer.writerow(row)

print("Archivo CSV generado correctamente.")