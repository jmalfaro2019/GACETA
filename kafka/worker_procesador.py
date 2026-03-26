import json
import os
from confluent_kafka import Consumer
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.output import text_from_rendered

# 1. Tu API Key de Gemini (¡Reemplázala con la tuya!)
# Esto le permite a Marker usar IA en la nube para leer imágenes y tablas
os.environ["GEMINI_API_KEY"] = "AIzaSyDy-3P4mrOKK2JKX_Opfy0Xx-MAgBGd4kE" 

# 2. Configuración de Marker
config = {
    "output_format": "markdown",
    "use_llm": True, # Activa el uso de IA para tablas/imágenes
    "llm_service": "marker.services.gemini.GoogleGeminiService" # Usa Gemini
}
config_parser = ConfigParser(config)

# 3. Inicializar el convertidor
print("Cargando modelo de Marker (esto es rápido)...")
converter = PdfConverter(
    config=config_parser.generate_config_dict(),
    artifact_dict=create_model_dict(),
    processor_list=config_parser.get_processors(),
    renderer=config_parser.get_renderer(),
    llm_service=config_parser.get_llm_service()
)

# 4. Configurar Kafka
configuracion_kafka = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'grupo_procesadores_marker_v1', 
    'auto.offset.reset': 'latest'
}

consumidor = Consumer(configuracion_kafka)
consumidor.subscribe(['gacetas_nuevas'])

# Crear carpeta de resultados
os.makedirs("documentos_markdown", exist_ok=True)
print("¡Worker de Marker listo! Esperando PDFs...\n")

try:
    while True:
        mensaje = consumidor.poll(1.0)

        if mensaje is None:
            continue
            
        if mensaje.error():
            print(f"Error de Kafka: {mensaje.error()}")
            continue

        datos = json.loads(mensaje.value().decode('utf-8'))
        
        if 'ruta' not in datos:
            continue

        ruta_pdf_original = datos['ruta']
        solo_nombre = os.path.basename(datos['archivo']) 
        nombre_base = solo_nombre.replace('.pdf', '')
        
        # Ruta real del PDF
        ruta_pdf_real = os.path.normpath(os.path.join("..", "gaceta_bot", ruta_pdf_original))
        
        print(f"📥 Procesando con Marker: {solo_nombre}")

        try:
            # 5. La conversión con Marker
            rendered = converter(ruta_pdf_real)
            texto_markdown, _, imagenes = text_from_rendered(rendered)
            
            # Guardar el Markdown
            ruta_md = os.path.normpath(os.path.join("documentos_markdown", f"{nombre_base}.md"))
            with open(ruta_md, "w", encoding="utf-8") as f:
                f.write(texto_markdown)
                
            # Opcional: Guardar las imágenes extraídas
            if imagenes:
                print(f"   📸 Se encontraron {len(imagenes)} imágenes. (Puedes configurar para guardarlas).")
                
            print(f"✅ ¡Éxito! Guardado en: {ruta_md}\n")
            
        except Exception as e:
            print(f"❌ Error convirtiendo: {e}\n")

except KeyboardInterrupt:
    print("Apagando el Worker...")
finally:
    consumidor.close()