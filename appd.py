from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from io import BytesIO
from dotenv import load_dotenv
import os
import json
import pandas as pd
from pydantic import BaseModel
from openai import OpenAI  # Usamos el SDK de OpenAI configurado para DeepSeek

app = FastAPI()

# Carga las variables de entorno (si las usas) o define directamente la clave y base_url
load_dotenv()
# En este ejemplo se define directamente la API key de DeepSeek
client = OpenAI(api_key="sk-843e1c4ca03f4c14b72c4e31bee09d3e", base_url="https://api.deepseek.com")

# Modelo de salida estructurado
class MedicalNoteExtraction(BaseModel):
    id_paciente: str
    prestacion: str
    nodulos: str               # 0(No), 1(Si)
    morfologia_nodulos: str    # 1(Ovalado), 2(Redondo), 3(Irregular)
    margenes_nodulos: str      # 1(Circunscritos), 2(Microlobulados), 3(Indistintos o mal definidos), 4(Obscurecidos), 5(Espiculados)
    densidad_nodulo: str       # 1(Densidad Grasa), 2(Baja Densidad (hipodenso)), 3(Igual Densidad (isodenso)), 4(Alta Densidad (hiperdenso))
    microcalcificaciones: str  # 0(No), 1(Si)
    calcificaciones_benignas: str   # 1(Cutaneas), 2(Vasculares), 3(Gruesas o Pop Corn), 4(Leño o Vara), 5(Redondas o puntiformes), 6(Anulares), 7(Distroficas), 8(Leche de Calcio), 9(Suturas)
    calcificaciones_sospechosas: str  # 1(Gruesas heterogeneas), 2(Amorfas), 3(Finas pleomorficas), 4(Lineas finas o lineales ramificadas)
    distribucion_calcificaciones: str # 1(Difusas), 2(Regionales), 3(Agrupadas (cumulo)), 4(Segmentaria), 5(Lineal)
    presencia_asimetrias: str        # 0(No), 1(Si)
    tipo_asimetria: str              # 1(Asimetria), 2(Asimetria global), 3(Asimetria focal), 4(Asimetria focal evolutiva)
    hallazgos_asociados: str         # 1(Retracción de la piel), 2(Retracción del pezón), 3(Engrosamiento de la piel), 4(Engrosamiento trabecular), 5(Adenopatias axilares)
    lateralidad_hallazgo: str        # 1(DERECHO), 2(IZQUIERDO), 3(BILATERAL)
    birads: str                      # 0, 1, 2, 3, 4A, 4B, 4C, 5, 6
    edad: str

@app.post("/process-medical-csv/")
async def process_medical_csv(
    file: UploadFile = File(...), 
    search_terms: str = Form(...)
):
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    content_bytes = await file.read()
    file_binary = BytesIO(content_bytes)
    df = pd.read_csv(file_binary, sep=';', encoding='utf-8', nrows=700)
    print("DF CARGADO")
    
    # Se define el prompt del sistema, incluyendo los parámetros y ejemplos de salida
    system_prompt = '''You are an expert at extracting structured data from medical notes. Follow these parameters:
- Nodulos: 0 (No), 1 (Si)
- Morfologia de los nodulos: 1 (Ovalado), 2 (Redondo), 3 (Irregular)
- Margenes de los nodulos: 1 (Circunscritos), 2 (Microlobulados), 3 (Indistintos o mal definidos), 4 (Obscurecidos), 5 (Espiculados)
- Densidad del nodulo: 1 (Densidad Grasa), 2 (Baja Densidad (hipodenso)), 3 (Igual Densidad (isodenso)), 4 (Alta Densidad (hiperdenso))
- Microcalcificaciones: 0 (No), 1 (Si)
- Calcificaciones tipicamente benignas: 1 (Cutaneas), 2 (Vasculares), 3 (Gruesas o Pop Corn), 4 (Leño o Vara), 5 (Redondas o puntiformes), 6 (Anulares), 7 (Distroficas), 8 (Leche de Calcio), 9 (Suturas)
- Calcificaciones morfologia sospechosa: 1 (Gruesas heterogeneas), 2 (Amorfas), 3 (Finas pleomorficas), 4 (Lineas finas o lineales ramificadas)
- Distribucion de las calcificaciones: 1 (Difusas), 2 (Regionales), 3 (Agrupadas (cumulo)), 4 (Segmentaria), 5 (Lineal)
- Presencia de asimetrias: 0 (No), 1 (Si)
- Tipo de asimetria: 1 (Asimetria), 2 (Asimetria global), 3 (Asimetria focal), 4 (Asimetria focal evolutiva)
- Hallazgos asociados: 1 (Retracción de la piel), 2 (Retracción del pezón), 3 (Engrosamiento de la piel), 4 (Engrosamiento trabecular), 5 (Adenopatias axilares)
- LATERALIDAD HALLAZGO: 1 (DERECHO), 2 (IZQUIERDO), 3 (BILATERAL)
- BIRADS: 0, 1, 2, 3, 4A, 4B, 4C, 5, 6
Only return the corresponding number or string for each field. If information is not available, return NULL.
Consider language variations and synonyms; pay special attention to keywords like MICROCALCIFICACIONES and CALCIFICACIONES BENIGNAS.

Example outputs:
Nodulos | Morfologia de los nodulos | Margenes Nodulos | Densidad Nodulo | Presencia Microcalcificaciones | Calcificaciones tipicamente benignas | Calcififcaciones morfologia sospechosa | Distribucion de las calcificaciones | Presencia de asimetrias | Tipo de asimetria | Hallazgos asociados | LATERALIDAD HALLAZGO | BIRADS | ID_PACIENTE
0. No   |                          |                  |                 | 1. Si                        | 5. Redondas o puntiformes          |                            | 2. Regionales             |                   |                 | 1. DERECHO             | 4a       | 000198
0. No   |                          |                  |                 | 0. No                        |                                  | 0. No                    |                         |                   |                 | 5. Adenopatias axilares| 1. DERECHO| 000198
0. No   |                          |                  |                 | 1. Si                        |                                  |                            |                         |                   |                 | 1. DERECHO             | 2        | 000198
0. No   |                          |                  |                 | 1. Si                        | 5. Redondas o puntiformes          |                            | 2. Regionales             |                   |                 | 1. DERECHO             | 2        | 000198
0. No   |                          |                  |                 | 1. Si                        | 5. Redondas o puntiformes          | 0. No                    |                         |                   |                 | 1. DERECHO             | 2        | 000198

Review the entire text before providing an output.
Output format example: nodulos=0, morfologia_nodulos=NULL, margenes_nodulos=NULL, densidad_nodulo=NULL, microcalcificaciones=1, calcificaciones_benignas=5, calcificaciones_sospechosas=NULL, distribucion_calcificaciones=2, presencia_asimetrias=NULL, tipo_asimetria=NULL, hallazgos_asociados=NULL, lateralidad_hallazgo=1, birads=4a, edad=80
'''

    structured_data = []

    for index, row in df.iterrows():
        prestacion = row['PRESTACION']
        id_paciente = row['ID_DOCUMENTO']
        edad = row['EDAD_EN_FECHA_ESTUDIO']
        notes = row['ESTUDIO']

        user_prompt = (
            f"Add ID_PACIENTE: {id_paciente}, PRESTACION: {prestacion}, EDAD: {edad} to the corresponding register. "
            f"Extract the following information from the notes: {notes}. Look for terms like {search_terms}."
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=False
        )

        # Se asume que la respuesta es un texto formateado en JSON que se ajusta al modelo MedicalNoteExtraction
        output_text = response.choices[0].message.content
        try:
            extracted_info = MedicalNoteExtraction.parse_raw(output_text)
        except Exception as e:
            # En caso de error al parsear, se guarda el output crudo para su revisión
            print(f"Error al parsear la respuesta: {e}\nOutput recibido: {output_text}")
            extracted_info = {"raw_output": output_text}
        print(extracted_info)
        # Se agrega el registro estructurado; si se parseó correctamente se usa .dict() sino se guarda el diccionario directo
        structured_data.append(extracted_info if isinstance(extracted_info, dict) else extracted_info.dict())
    
    with open('structured_data.json', 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=4)
    
    return {"structured_data": structured_data}
