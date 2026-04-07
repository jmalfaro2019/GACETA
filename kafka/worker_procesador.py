import json
import os
from confluent_kafka import Consumer, KafkaException
import easyocr
import numpy as np
import torch
import fitz  # For columns and images
import pdfplumber  # The table expert
import io
from PIL import Image
import psycopg2
from groq_parser import parse_markdown_to_json

def table_to_markdown(table_data):
    if not table_data or not table_data[0]:
        return ""
    
    cleaned_data = []
    for row in table_data:
        cleaned_row = [str(cell).replace('\n', ' ').strip() if cell is not None else "" for cell in row]
        cleaned_data.append(cleaned_row)
        
    md = ""
    headers = cleaned_data[0]
    md += "| " + " | ".join(headers) + " |\n"
    md += "|" + "|".join(["---"] * len(headers)) + "|\n"
    
    for row in cleaned_data[1:]:
        md += "| " + " | ".join(row) + " |\n"
        
    return md + "\n"

def boxes_intersect(box1, box2):
    """
    Checks whether two bounding boxes intersect or overlap.
    Format: (x0, y0, x1, y1)
    """
    return not (box1[2] <= box2[0] or  # box1 is to the left of box2
                box1[0] >= box2[2] or  # box1 is to the right of box2
                box1[3] <= box2[1] or  # box1 is above box2
                box1[1] >= box2[3])    # box1 is below box2

def process_pdf_master(pdf_path):
    full_text = []
    
    # Open the PDF with BOTH libraries
    doc_fitz = fitz.open(pdf_path)
    pdf_plumb = pdfplumber.open(pdf_path)
    
    for page_num in range(len(doc_fitz)):
        print(f"Starting page {page_num + 1}...")
        page_content = []
        page_fitz = doc_fitz[page_num]
        page_plumb = pdf_plumb.pages[page_num]

        table_bboxes = []

        # Extract tables
        tables = page_plumb.find_tables()
        for i, table in enumerate(tables):
            table_bboxes.append(table.bbox)
            table_data = table.extract()
            md_table = table_to_markdown(table_data)
            page_content.append(f"\n> **Table {i+1} detected:**\n\n{md_table}")

        # Extract images
        print(f"Extracting images...")
        image_list = page_fitz.get_images(full=True)
        for i, img in enumerate(image_list):
            xref = img[0]
            try:
                base_image = doc_fitz.extract_image(xref)
                image_bytes = base_image["image"]

                image = Image.open(io.BytesIO(image_bytes))

                # Filter images by size to skip logos and noise
                width, height = image.size
                if width < 50 or height < 50:
                    continue

                # Resize very large images to prevent memory issues
                if width > 2000 or height > 2000:
                    image.thumbnail((2000, 2000))

                if image.mode != 'RGB':
                    image = image.convert('RGB')
                img_array = np.array(image)

                ocr_results = reader.readtext(img_array, detail=0)
                ocr_text = "\n".join(ocr_results)

                if ocr_text.strip():
                    page_content.append(f"\n> *Text from image {i+1}:*\n> {ocr_text}\n")
            except Exception as e:
                print(f"Image warning on page {page_num + 1}: {e}")

        # Extract text blocks
        print(f"Extracting text...")
        blocks = page_fitz.get_text("blocks", sort=True)
        normal_text_pieces = []

        for b in blocks:
            block_bbox = (b[0], b[1], b[2], b[3])
            block_text = b[4]
            block_type = b[6]  # 0=text, 1=image

            if block_type == 0:
                is_inside_table = False
                for t_box in table_bboxes:
                    if boxes_intersect(block_bbox, t_box):
                        is_inside_table = True
                        break

                if not is_inside_table:
                    normal_text_pieces.append(block_text)

        if normal_text_pieces:
            page_content.insert(0, "\n\n".join(normal_text_pieces))

        full_text.append(f"## Page {page_num + 1}\n\n" + "\n".join(page_content) + "\n")
        
    doc_fitz.close()
    pdf_plumb.close()

    return "\n---\n".join(full_text)


# Automatic hardware detection
if torch.cuda.is_available():
    print("NVIDIA GPU (CUDA) detected")
    use_gpu = True
else:
    print("Using CPU")
    use_gpu = False

print("Loading EasyOCR model...")
reader = easyocr.Reader(['es', 'en'], gpu=use_gpu)

# Kafka configuration
kafka_config = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    'group.id': os.getenv('GROUP_ID', 'pdf_processors_group_v4'),
    'auto.offset.reset': 'latest',
    'max.poll.interval.ms': 900000  # 15 minutes tolerance for slow OCR processing
}

consumer = Consumer(kafka_config)
consumer.subscribe([os.getenv('TOPIC', 'new_gazettes')])

os.makedirs("documents_markdown", exist_ok=True)
print("Master hybrid worker (PDFPlumber + PyMuPDF + EasyOCR) ready!\n")


# Kafka main loop
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
        real_pdf_path = os.path.normpath(os.path.join("..", "gaceta_bot", original_pdf_path))

        print(f"Processing: {file_name_only}")

        try:
            # 1. Extraction du texte
            markdown_text = process_pdf_master(real_pdf_path)
            
            # 2. AI Processing (Groq)
            print(f"Sending '{base_name}' to Groq for parsing...")
            structured_data = parse_markdown_to_json(markdown_text)
            
            # 3. Sauvegarde dans un fichier local 
            json_path = os.path.normpath(os.path.join("documents_json", f"{base_name}.json"))
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            
            # 2. Sauvegarde dans un fichier local (ton code d'origine)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(structured_data, f, ensure_ascii=False, indent=4)
                print(f"Success! Saved structured JSON to: {json_path}")
            
            # ---------------------------------------------------------
            # 3. INSERTION DANS PARADEDB (NOUVEAU CODE)
            # ---------------------------------------------------------
            try:
                # On ouvre la connexion
                conn = psycopg2.connect(
                    dbname="gaceta_db",
                    user="admin",
                    password="secret",
                    host="localhost",
                    port="5433"
                )
                cursor = conn.cursor()
                
                # Convertimos el diccionario a un string JSON para guardarlo en la DB
                json_para_db = json.dumps(structured_data)
                # On insère le titre (base_name) et le contenu
                insert_query = """
                    INSERT INTO documents (titre, contenu_json)
                    VALUES (%s, %s);
                """
                cursor.execute(insert_query, (base_name, json_para_db))
                
                # On valide et on ferme
                conn.commit()
                cursor.close()
                conn.close()
                print(f"Success! Inserted '{base_name}' into ParadeDB.")
                
            except Exception as db_error:
                print(f"Database error while inserting '{base_name}': {db_error}")
            # ---------------------------------------------------------

        except Exception as e:
            print(f"Error converting: {e}")

except KeyboardInterrupt:
    print("\nShutting down worker...")
finally:
    consumer.close()

