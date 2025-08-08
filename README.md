# Extracción de Datos de Notas Médicas

Este repositorio contiene dos aplicaciones basadas en FastAPI para extraer información estructurada de notas médicas en archivos CSV. 

- `app.py`: Utiliza la API de OpenAI para el procesamiento de texto.
- `local.py`: Utiliza un modelo alojado localmente a través de Ollama.

## Requisitos

Antes de ejecutar cualquiera de las aplicaciones, asegúrate de tener las siguientes dependencias instaladas:

Python v12 o superior con las siguientes librerías:

```bash
pip install fastapi uvicorn python-dotenv openai pandas pydantic requests
```

Si utilizas `local.py`, asegúrate de tener **Ollama** instalado y ejecutándose en tu máquina. Puedes descargarlo desde [Ollama](https://ollama.com/).

## Configuración

Debes crear un archivo `.env` en el directorio raíz del proyecto con las siguientes variables:

```ini
# Para app.py (requiere clave de API de OpenAI)
OPENAI_API_KEY=tu_clave_de_api

# Para local.py (requiere servidor Ollama)
OLLAMA_API_URL=http://localhost:11434/api
```

## Uso

### 1. Ejecutar con OpenAI (`app.py`)

Para iniciar el servidor FastAPI con OpenAI:

```bash
uvicorn app:app --reload
```

Esto iniciará un servidor en `http://127.0.0.1:8000`.

### 2. Ejecutar con Ollama (`local.py`)

Para usar el modelo Phi-4 de Ollama en local:

```bash
uvicorn local:app --reload
```

Asegúrate de que **Ollama está corriendo** en tu máquina antes de ejecutar este comando.

## Uso de la API

Ambas aplicaciones exponen un endpoint para procesar archivos CSV:

```
POST /process-medical-csv/
```

**Parámetros:**
- `file`: Archivo CSV (debe contener columnas `ID_DOCUMENTO`, `PRESTACION`, `EDAD_EN_FECHA_ESTUDIO`, `ESTUDIO`).
- `search_terms`: Términos clave para buscar en las notas médicas.

Ejemplo de uso con `cURL`:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/process-medical-csv/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@archivo.csv' \
  -F 'search_terms="nodulos, calcificaciones"'
```

El resultado es un JSON con los datos extraídos.

Ejemplo de uso con `uvicorn local:app --reload`

- En la dirección **127.0.0.1:8000/docs** se encontrará la siguiente interfaz:
![alt text](/images/uvicorn.png)

- Se debe seleccior el endpoint POST de **/process-medical-csv/** y dar en la opción de **Try out**:
![alt text](/images/endpoint.png)

- Se de debe subir el archivo en csv con el formato solicitado y dar en execute:
![alt text](/images/upload%20file.png)





## Contacto

Si tienes preguntas o sugerencias, abre un issue en este repositorio.
