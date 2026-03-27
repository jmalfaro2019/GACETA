import json
import os
from confluent_kafka import Consumer
import pdfplumber
import easyocr
import numpy as np
import torch # <- Añadimos PyTorch para detectar el hardware

# --- DETECCIÓN AUTOMÁTICA DE HARDWARE ---
if torch.cuda.is_available():
    print("🚀 ¡GPU NVIDIA (CUDA) detected!")
    usar_gpu = True
else:
    print("💻 Using CPU")
    usar_gpu = False

print("EasyOCR reader")
reader = easyocr.Reader(['es', 'en'], gpu=usar_gpu)

# 2. Kafka configuration
kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'pdf_processors_group_v2',  # Changed ID to avoid conflicts with previous offset
    'auto.offset.reset': 'latest'
}

consumer = Consumer(kafka_config)
consumer.subscribe(['new_gazettes'])

# Create output folder
os.makedirs("documents_markdown", exist_ok=True)
print("✓ Hybrid worker (PDFPlumber + EasyOCR) ready! Waiting for PDFs...\n")

try:
    while True:
        message = consumer.poll(1.0)

        if message is None:
            continue
            
        if message.error():
            print(f"Kafka error: {message.error()}")
            continue

        data = json.loads(message.value().decode('utf-8'))
        
        if 'path' not in data:
            continue

        original_pdf_path = data['path']
        file_name_only = os.path.basename(data.get('file', original_pdf_path)) 
        base_name = file_name_only.replace('.pdf', '')
        
        # Real path to the PDF
        real_pdf_path = os.path.normpath(os.path.join("..", "gaceta_bot", original_pdf_path))
        
        print(f"📥 Processing: {file_name_only}")

        try:
            # 3. Conversion using hybrid approach
            markdown_text = process_pdf_hybrid(real_pdf_path)
            
            # Save Markdown
            md_path = os.path.normpath(os.path.join("documents_markdown", f"{base_name}.md"))
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(markdown_text)
                
            print(f"✅ Success! Saved to: {md_path}\n")
            
        except Exception as e:
            print(f"❌ Error converting: {e}\n")

except KeyboardInterrupt:
    print("\nShutting down worker...")
finally:
    consumer.close()

def table_to_markdown(table_data):
    """
    Convierte una lista de listas (tabla de pdfplumber) en una tabla Markdown limpia.
    """
    if not table_data or not table_data[0]:
        return ""
    
    # Limpiar saltos de línea dentro de las celdas para no romper el Markdown
    cleaned_data = []
    for row in table_data:
        cleaned_row = [str(cell).replace('\n', ' ').strip() if cell is not None else "" for cell in row]
        cleaned_data.append(cleaned_row)
        
    md = ""
    # Cabeceras
    headers = cleaned_data[0]
    md += "| " + " | ".join(headers) + " |\n"
    md += "|" + "|".join(["---"] * len(headers)) + "|\n"
    
    # Filas
    for row in cleaned_data[1:]:
        md += "| " + " | ".join(row) + " |\n"
        
    return md + "\n"

def process_pdf_hybrid(pdf_path):
    full_text = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_content = []
            bboxes_to_exclude = [] # Zonas de la página que no queremos leer como texto normal
            
            # 1. PROCESAR TABLAS
            tables = page.find_tables()
            for i, table in enumerate(tables):
                bboxes_to_exclude.append(table.bbox) # Guardar las coordenadas de la tabla
                table_data = table.extract()
                md_table = table_to_markdown(table_data)
                page_content.append(f"\n> **Tabla {i+1} detectada:**\n\n{md_table}")

            # 2. PROCESAR IMÁGENES CON EASYOCR
            if page.images:
                for i, img in enumerate(page.images):
                    bbox = (img['x0'], img['top'], img['x1'], img['bottom'])
                    bboxes_to_exclude.append(bbox) # Guardar coordenadas de la imagen
                    
                    try:
                        crop = page.within_bbox(bbox)
                        img_obj = crop.to_image(resolution=300)
                        img_array = np.array(img_obj.original)
                        
                        ocr_results = reader.readtext(img_array, detail=0)
                        ocr_text = "\n".join(ocr_results)
                        
                        if ocr_text.strip():
                            page_content.append(f"\n> *Texto de imagen {i+1}:*\n> {ocr_text}\n")
                    except Exception as e:
                        print(f"  ⚠️ Advertencia imagen pág {page_num + 1}: {e}")

            # 3. EXTRAER TEXTO NORMAL (COLUMNAS)
            # Filtramos la página para que ignore las zonas donde ya sabemos que hay tablas o imágenes
            def is_outside_bboxes(obj):
                if obj.get('object_type') != 'char': 
                    return True
                ox0, otop, ox1, obottom = obj['x0'], obj['top'], obj['x1'], obj['bottom']
                
                for (bx0, btop, bx1, bbottom) in bboxes_to_exclude:
                    # Si el carácter choca con las coordenadas a excluir, lo ignoramos
                    if not (ox1 <= bx0 or ox0 >= bx1 or obottom <= btop or otop >= bbottom):
                        return False
                return True

            clean_page = page.filter(is_outside_bboxes)
            
            # ¡La magia ocurre aquí! laparams={} activa el análisis de columnas
            normal_text = clean_page.extract_text(laparams={}) 
            
            if normal_text:
                # Insertamos el texto principal al principio, seguido de las tablas e imágenes extraídas
                page_content.insert(0, normal_text)
                
            full_text.append(f"## Página {page_num + 1}\n\n" + "\n".join(page_content) + "\n")
            print(f"  - Procesada página {page_num + 1}/{len(pdf.pages)} (Encontradas {len(tables)} tablas)")
            
    return "\n---\n".join(full_text)

def process_pdf_hybrid(pdf_path):
    """
    Extracts native text and applies OCR to embedded images.
    """
    full_text = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_content = []
            
            # A. Extract normal (native PDF) text
            normal_text = page.extract_text()
            if normal_text:
                page_content.append(normal_text)
                
            # B. Find images, crop them, and apply OCR
            if page.images:
                for img in page.images:
                    # Get image coordinates (bounding box)
                    bbox = (img['x0'], img['top'], img['x1'], img['bottom'])
                    
                    try:
                        # Crop only the part of the page containing the image
                        crop = page.within_bbox(bbox)
                        
                        # Convert to high-resolution image and then to NumPy array
                        img_obj = crop.to_image(resolution=300)
                        img_array = np.array(img_obj.original)
                        
                        # Apply OCR
                        ocr_results = reader.readtext(img_array, detail=0)
                        ocr_text = "\n".join(ocr_results)
                        
                        if ocr_text.strip():
                            # Add a small format to distinguish image text
                            page_content.append(f"\n> *Text extracted from image:*\n> {ocr_text}\n")
                            
                    except Exception as e:
                        print(f"  ⚠️ Warning: Could not process an image on page {page_num + 1}: {e}")
            
            # Combine all page content
            full_text.append(f"## Page {page_num + 1}\n\n" + "\n".join(page_content) + "\n")
            print(f"  - Processed page {page_num + 1}/{len(pdf.pages)}")
            
    return "\n---\n".join(full_text)

