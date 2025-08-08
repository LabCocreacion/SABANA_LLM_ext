from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from io import BytesIO
from dotenv import load_dotenv
import os
import requests
import pandas as pd
from typing import List
from pydantic import BaseModel
import json


app = FastAPI()

load_dotenv()
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")

class MedicalNoteExtraction(BaseModel):
    id_paciente: str
    prestacion: str
    nodulos: str  # 0(No), 1(Si)
    morfologia_nodulos: str  # 1(Ovalado), 2(Redondo), 3(Irregular)
    margenes_nodulos: str  # 1(Circunscritos), 2(Microlobulados), 3(Indistintos o mal definidos), 4(Obscurecidos), 5(Espiculados)
    densidad_nodulo: str  # 1(Densidad Grasa), 2(Baja Densidad (hipodenso)), 3(Igual Densidad (isodenso)), 4(Alta Densidad (hiperdenso))
    microcalcificaciones: str  # 0(No), 1(Si)
    calcificaciones_benignas: str  # 1(Cutaneas), 2(Vasculares), 3(Gruesas o Pop Corn), 4(Leño o Vara), 5(Redondas o puntiformes), 6(Anulares), 7(Distroficas), 8(Leche de Calcio), 9(Suturas)
    calcificaciones_sospechosas: str  # 1(Gruesas heterogeneas), 2(Amorfas), 3(Finas pleomorficas), 4(Lineas finas o lineales ramificadas)
    distribucion_calcificaciones: str  # 1(Difusas), 2(Regionales), 3(Agrupadas (cumulo)), 4(Segmentaria), 5(Lineal)
    presencia_asimetrias: str  # 0(No), 1(Si)
    tipo_asimetria: str  # 1(Asimetria), 2(Asimetria global), 3(Asimetria focal), 4(Asimetria focal evolutiva)
    hallazgos_asociados: str  # 1(Retracción de la piel), 2(Retracción del pezón), 3(Engrosamiento de la piel), 4(Engrosamiento trabecular), 5(Adenopatias axilares)
    lateralidad_hallazgo: str  # 1(DERECHO), 2(IZQUIERDO), 3(BILATERAL)
    birads: str  # 0, 1, 2, 3, 4A, 4B, 4C, 5, 6
    edad: str


def parse_phi4_response(response_text):
    """Parse the Phi-4 response text into a MedicalNoteExtraction object."""
    extraction = MedicalNoteExtraction(
        id_paciente="",
        prestacion="",
        nodulos="NULL",
        morfologia_nodulos="NULL",
        margenes_nodulos="NULL",
        densidad_nodulo="NULL",
        microcalcificaciones="NULL",
        calcificaciones_benignas="NULL",
        calcificaciones_sospechosas="NULL",
        distribucion_calcificaciones="NULL",
        presencia_asimetrias="NULL",
        tipo_asimetria="NULL",
        hallazgos_asociados="NULL",
        lateralidad_hallazgo="NULL",
        birads="NULL",
        edad="NULL"
    )
    
    # Extract key-value pairs from response text
    for line in response_text.strip().split(','):
        if '=' in line:
            key, value = line.strip().split('=', 1)
            key = key.strip()
            value = value.strip()
            
            if hasattr(extraction, key):
                setattr(extraction, key, value)
    
    return extraction

@app.post("/process-medical-csv/")
async def process_medical_csv(
    file: UploadFile = File(...), 
    search_terms: str = Form(...)
):
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    content = await file.read()
    file_binary = BytesIO(content)
    df = pd.read_csv(file_binary, sep=';', encoding='utf-8', nrows=700)
    print("DF CARGADO")
    
    system_content = '''You are an expert at extracting structured data from medical notes. Follow the same parameters: -Nodulos: 0(No) 1(Si) 
    -Morfologia de los nodulos:1(Ovalado) 2(Redondo) 3(Irregular) -Margenes de los nodulos: 1(Circunscritos), 2(Microlobulados), 3(Indistintos o mal definidos), 4(Obscurecidos), 5(Espiculados) 
    -Densidad del nodulo: 1(Densidad Grasa), 2(Baja Densidad (hipodenso)), 3(Igual Densidad (isodenso)), 4(Alta Densidad (hiperdenso))  
    -Microcalcificaciones: 0(No) 1(Si) -Calcificaciones tipicamente benignas: 1(Cutaneas), 2(Vasculares), 3(Gruesas o Pop Corn), 4(Leño o Vara), 5(Redondas o puntiformes), 6(Anulares), 7(Distroficas), 8(Leche de Calcio), 9(Suturas)  
    -Calsificaciones morfologia sospechosa: 1(Gruesas heterogeneas), 2(Amorfas), 3(Finas pleomorficas), 4(Lineas finas o lineales ramificadas)  
    -Distribicion de las calcificaciones: 1(Difusas), 2(Regionales), 3(Agrupadas (cumulo)), 4(Segmentaria), 5(Lineal) 
    -Presencia de asimetrias: 0(No), 1(Si) -Tipo de asimetria: 1(Asimetria), 2(Asimetria global), 3(Asimetria focal), 4(Asimetria focal evolutiva)
    -Hallazgos asociados: 1(Retracción de la piel), 2(Retracción del pezón), 3(Engrosamiento de la piel), 4(Engrosamiento trabecular), 5(Adenopatias axilares)
    -LATERALIDAD HALLAZGO:1(DERECHO), 2(IZQUIERDO), 3(BILATERAL) -BIRADS: 0, 1, 2, 3, 4A, 4B, 4C, 5, 6. 
    Solo devuelve el numero, busca en todo el texto, ten en cuenta que cada nota puede contener variaciones del lenguaje y que pueden haber palabras usadas como sinonimos, 
    y no necesariamente toda la información está disponible, si ni está disponible escribe NULL, terminos como MICROCALCIFICACIONES y CALCIFICACIONES BENIGNAS 
    son importantes para la extracción de información y si existen calcificaciones benignas o no benignas son microcalcificaciones de igual manera. 
    Revisa todo el texto antes de dar un output. Responde solo con los valores de los campos en formato id_paciente=xxx, prestacion=xxx, nodulos=x, etc. 
    No incluyas explicaciones adicionales, solo el resultado.'''

    structured_data = []

    for index, row in df.iterrows():
        presentacion = row['PRESTACION']
        id_paciente = row['ID_DOCUMENTO']
        edad = row['EDAD_EN_FECHA_ESTUDIO']
        notes = row['ESTUDIO']
        
        user_message = f"Add ID_PACIENTE: {id_paciente}, PRESTACION: {presentacion}, EDAD: {edad} to each corresponding register. Extract the following information from the notes: {notes}. Look for terms like {search_terms}."
        
        # Call Ollama API with Phi-4 model
        response = requests.post(
            f"{OLLAMA_API_URL}/chat",
            json={
                "model": "phi4",
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_message}
                ],
                "stream": False
            },
            proxies={"http": None, "https": None}  # Disable proxies
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Ollama API error: {response.text}")
        
        result = response.json()
        answer_text = result["message"]["content"]
        
        # Parse the response into a structured format
        extracted_info = parse_phi4_response(answer_text)
        
        # Set the ID and prestacion
        extracted_info.id_paciente = id_paciente
        extracted_info.prestacion = presentacion
        extracted_info.edad = str(edad)
        
        print(extracted_info)
        structured_data.append(extracted_info.model_dump())
    
    with open('structured_data.json', 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=4)
        
    return {"structured_data": structured_data}