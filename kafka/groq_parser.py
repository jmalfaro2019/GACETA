import os
import json
import re
import time
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize the client
client = Groq()

def remove_base64_images(text: str) -> str:
    """
    Finds and removes massive base64 image strings from the markdown.
    This prevents token limits from exploding due to embedded images.
    """
    # Matches markdown image format containing base64 data
    return re.sub(r'!\[.*?\]\(data:image/.*?;base64,.*?\)', '[IMAGE REMOVED]', text)

def parse_markdown_to_json(markdown_text: str) -> dict:
    """
    Takes a Markdown text, cleans base64 images, chunks it if necessary, 
    uses Groq to parse it, and returns a merged structured dictionary.
    """
    # 1. Definición del rol y contexto del agente
    prompt_rol = """
    Eres un agente de inteligencia artificial experto en análisis de datos legislativos y derecho parlamentario de Colombia. 
    Tienes una precisión analítica impecable y tu función es procesar documentos oficiales de la Gaceta del Congreso.
    IMPORTANTE: El texto proviene de un Markdown ruidoso con problemas de escritura, errores ortográficos, palabras cortadas y ruido de OCR. 
    Debes interpretar el contenido de manera inteligente para corregir estos errores durante la extracción.
    """

    # 2. Descripción general de la tarea
    prompt_tarea = """
    Tu tarea es leer el texto del documento adjunto, identificar qué tipo de archivo es (Proyecto de Ley, Ponencia, Acta de Sesión, etc.) y extraer la información clave. 
    Debes consolidar esta información y retornar ÚNICAMENTE un objeto JSON válido, sin texto adicional.
    """

    # 3. Estructura de Metadatos Generales (Siempre requerida)
    prompt_metadatos = """
    El JSON de salida siempre debe contener un bloque llamado "metadatos_generales" con la siguiente estructura:
    "metadatos_generales": {
        "numero_gaceta": "Número de la gaceta si está disponible, de lo contrario null",
        "fecha_publicacion": "Formato YYYY-MM-DD",
        "tipo_documento": "Clasifica el documento (Ej: Proyecto de Ley, Ponencia, Acta de Sesión, Citación, Objeción, Otro)",
        "titulo_principal": "Título literal del documento",
        "autores_o_firmantes": ["Lista de nombres"],
        "palabras_clave": ["Tema 1", "Tema 2", "Tema 3"],
        "resumen_ia": "Un resumen ejecutivo muy profesional de aproximadamente 2 párrafos",
        "contenido_limpio": "El texto principal del documento corregido gramaticalmente y estructurado, eliminando ruido de encabezados/pies de página."
    }
    """

    # 4. Estructura de Detalles Específicos (Dinámica)
    prompt_detalles = """
    Además, el JSON debe incluir un bloque llamado "detalles_especificos" que cambiará según el "tipo_documento" identificado:

    - Si es un 'Proyecto de Ley': Extrae "numero_proyecto", "camara_origen", "argumentos_principales" (lista), e "impacto_fiscal".
    - Si es una 'Ponencia': Extrae "tipo_ponencia" (Positiva/Negativa/Modificatoria), "debate_correspondiente", "cambios_clave_propuestos", y "decision_solicitada".
    - Si es una 'Citación a Control Político': Extrae "funcionarios_citados", "tema_del_debate", y "resumen_cuestionario".
    - Si es una 'Objeción Presidencial': Extrae "tipo_objecion", "articulos_objetados", y "argumento_gobierno".

    - IMPORTANTE: Si es un 'Acta de Sesión', tu prioridad es la vigilancia política. Extrae:
    "tipo_sesion": "Plenaria o Comisión",
    "fecha_sesion": "YYYY-MM-DD",
    "temas_debatidos": ["Lista de proyectos o temas"],
    "votaciones": [
        {
            "asunto_votado": "Título del proyecto o artículo votado",
            "votos_a_favor": ["Nombre y Apellido del congresista 1", "Nombre 2..."],
            "votos_en_contra": ["Nombre y Apellido del congresista 1", "Nombre 2..."],
            "ausencias_o_abstenciones": ["Nombre y Apellido del congresista 1", "Nombre 2..."]
        }
    ]
    """

    # 5. Reglas estrictas y restricciones (Guardrails)
    prompt_reglas = """
    REGLAS ESTRICTAS:
    1. No inventes nombres. Si un congresista no aparece explícitamente en la lista de votación o asistencia del texto, no lo incluyas.
    2. Si una información no está en el texto, asigna el valor 'null' (no uses 'N/A' ni 'No especificado').
    3. El formato de salida debe ser estrictamente JSON.
    """

    system_prompt = (prompt_rol + "\n" +
        prompt_tarea + "\n" +
        prompt_metadatos + "\n" +
        prompt_detalles + "\n" +
        prompt_reglas + "\n" +
        "A continuación, el texto del documento a analizar:\n\n")

    # 1. Clean base64 images to drastically reduce token size
    cleaned_text = remove_base64_images(markdown_text)

    # 2. Setup chunking (Groq limit is 12k TPM. ~30,000 characters is ~7,500 tokens)
    chunk_size = 30000 
    chunks = [cleaned_text[i:i+chunk_size] for i in range(0, len(cleaned_text), chunk_size)]
    
    combined_result = {
        "metadatos_generales": {
            "numero_gaceta": None,
            "fecha_publicacion": None,
            "tipo_documento": None,
            "titulo_principal": "",
            "autores_o_firmantes": [],
            "palabras_clave": [],
            "resumen_ia": "",
            "contenido_limpio": ""
        },
        "detalles_especificos": {}
    }

    for index, chunk in enumerate(chunks):
        try:
            print(f"Sending chunk {index + 1} of {len(chunks)} to Groq...")
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chunk}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}, 
                temperature=0.1, 
            )
            
            # Parse the response for this specific chunk
            chunk_json = json.loads(chat_completion.choices[0].message.content)
            
            # --- MERGE METADATOS ---
            meta = chunk_json.get("metadatos_generales", {})
            if meta:
                # Titulo y otros campos simples se toman del primer chunk o se concatenan si tienen sentido
                if not combined_result["metadatos_generales"]["titulo_principal"]:
                    combined_result["metadatos_generales"]["titulo_principal"] = meta.get("titulo_principal", "")
                    combined_result["metadatos_generales"]["numero_gaceta"] = meta.get("numero_gaceta")
                    combined_result["metadatos_generales"]["fecha_publicacion"] = meta.get("fecha_publicacion")
                    combined_result["metadatos_generales"]["tipo_documento"] = meta.get("tipo_documento")

                # Listas se extienden (usamos "or []" por si la IA devuelve null)
                combined_result["metadatos_generales"]["autores_o_firmantes"].extend(meta.get("autores_o_firmantes") or [])
                combined_result["metadatos_generales"]["palabras_clave"].extend(meta.get("palabras_clave") or [])
                
                # Texto largo se concatena (usamos "or ''" por si la IA devuelve null)
                combined_result["metadatos_generales"]["resumen_ia"] += (meta.get("resumen_ia") or "") + " "
                combined_result["metadatos_generales"]["contenido_limpio"] += (meta.get("contenido_limpio") or "") + "\n\n"

            # --- MERGE DETALLES ESPECIFICOS ---
            detalles = chunk_json.get("detalles_especificos") or {}
            if detalles:
                for key, value in detalles.items():
                    if value is None: continue # Skip if this specific detail is null
                    
                    if key not in combined_result["detalles_especificos"]:
                        combined_result["detalles_especificos"][key] = value
                    else:
                        # Si ya existe, decidimos como unir según el tipo
                        if isinstance(value, list) and isinstance(combined_result["detalles_especificos"][key], list):
                            combined_result["detalles_especificos"][key].extend(value or [])
                        elif isinstance(value, str) and isinstance(combined_result["detalles_especificos"][key], str):
                            if value and value not in combined_result["detalles_especificos"][key]:
                                combined_result["detalles_especificos"][key] += " " + value

            # 3. Respect Rate Limits: Pause before sending the next chunk
            if index < len(chunks) - 1:
                print("Waiting 60 seconds to reset Groq's TPM limit...")
                time.sleep(60) 
                
        except Exception as e:
            print(f"CRITICAL: Error processing chunk {index + 1} with Groq: {e}")
            # Raising the exception instead of returning partial results
            # to prevent saving incomplete data.
            raise e
            
    # Final cleanup of the merged data
    meta_fin = combined_result["metadatos_generales"]
    meta_fin["titulo_principal"] = meta_fin["titulo_principal"].strip()
    meta_fin["autores_o_firmantes"] = list(set(meta_fin["autores_o_firmantes"]))
    meta_fin["palabras_clave"] = list(set(meta_fin["palabras_clave"]))
    meta_fin["resumen_ia"] = meta_fin["resumen_ia"].strip()
    meta_fin["contenido_limpio"] = meta_fin["contenido_limpio"].strip()

    return combined_result