import json
import os
import pika
from dotenv import load_dotenv

load_dotenv()
import easyocr
import numpy as np
import torch
import fitz  # For columns and images
import pdfplumber  # The table expert
import io
import sys
from PIL import Image
import psycopg2
from groq_parser import parse_markdown_to_json
import requests
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

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

# RabbitMQ configuration
rabbitmq_url = os.getenv('CLOUDAMQP_URL', 'amqp://guest:guest@localhost/%2f')
params = pika.URLParameters(rabbitmq_url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

queue_name = 'new_gazettes'
channel.queue_declare(queue=queue_name, durable=True)

# Important: To avoid overloading one worker, we tell RabbitMQ to only
# send one message at a time to this worker.
channel.basic_qos(prefetch_count=1)

os.makedirs("documents_markdown", exist_ok=True)
print(f"Master hybrid worker ready! Listening on RabbitMQ queue: {queue_name}\n")


def callback(ch, method, properties, body):
    try:
        data = json.loads(body.decode('utf-8'))
        if 'path' not in data:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        original_pdf_path = data.get('path')
        file_url = data.get('url')
        file_name_only = os.path.basename(data.get('file', original_pdf_path or "document.pdf"))
        base_name = file_name_only.replace('.pdf', '')
        
        print(f"[*] Processing: {file_name_only}")

        # Distributed file handling: If a URL is provided, we download it first
        temp_pdf_file = None
        if file_url:
            print(f"  - Downloading PDF from: {file_url}")
            try:
                # Create a temporary file that will be deleted after processing
                temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                response = requests.get(file_url, stream=True)
                if response.status_code == 200:
                    for chunk in response.iter_content(chunk_size=8192):
                        temp_pdf.write(chunk)
                    temp_pdf.close()
                    real_pdf_path = temp_pdf.name
                    temp_pdf_file = temp_pdf.name
                else:
                    print(f"  - Error downloading PDF: status {response.status_code}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return
            except Exception as download_error:
                print(f"  - Download exception: {download_error}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
        else:
            # Fallback to local path for development/local testing
            real_pdf_path = os.path.normpath(os.path.join("..", "gaceta_bot", original_pdf_path))

        # 1. Extraction du texte
        markdown_text = process_pdf_master(real_pdf_path)
        
        # 1.5 Sauvegarde du Markdown (Checkpoint)
        md_path = os.path.normpath(os.path.join("documents_markdown", f"{base_name}.md"))
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        print(f"  - Markdown checkpoint saved to: {md_path}")
        
        # 2. AI Processing (Groq)
        print(f"Sending '{base_name}' to Groq for parsing...")
        try:
            structured_data = parse_markdown_to_json(markdown_text)
        except Exception as ai_error:
            print(f"FATAL ERROR: AI processing failed for '{base_name}': {ai_error}")
            print("Stopping program to ensure data integrity and avoid wasting API resources.")
            # We don't ACK the message here so it can be retried later, then exit
            sys.exit(1)
        
        # 3. Sauvegarde dans un fichier local 
        json_path = os.path.normpath(os.path.join("documents_json", f"{base_name}.json"))
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(structured_data, f, ensure_ascii=False, indent=4)
            print(f"Success! Saved structured JSON to: {json_path}")
        
        # 4. INSERTION DANS PARADEDB
        try:
            cursor = conn.cursor()
            ai_title = structured_data.get("metadatos_generales", {}).get("titulo_principal", base_name)
            json_para_db = json.dumps(structured_data)
            
            insert_query = """
                INSERT INTO documents (titre, contenu_json)
                VALUES (%s, %s);
            """
            cursor.execute(insert_query, (ai_title, json_para_db))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Success! Inserted '{ai_title}' into ParadeDB.")
        except Exception as db_error:
            print(f"Database error while inserting '{base_name}': {db_error}")

        # Finalement, on confirme la lecture du message
        print(f"[x] Done processing '{file_name_only}'\n")
        
        # Cleanup temporary file if downloaded
        if temp_pdf_file and os.path.exists(temp_pdf_file):
            os.remove(temp_pdf_file)
            print(f"  - Cleaned up temp file: {temp_pdf_file}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Non-fatal error processing document: {e}")
        # Even on error, we ACK or NACK to avoid infinite loop of fails
        # Here we ACK to remove it from queue since it's probably a corrupt PDF
        ch.basic_ack(delivery_tag=method.delivery_tag)


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"OK - Worker is running")

def run_health_check_server():
    """Runs a minimal HTTP server on port 7860 to satisfy Hugging Face's health check."""
    port = int(os.getenv("PORT", 7860))
    server_address = ('', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f"[*] Health check server started on port {port}")
    httpd.serve_forever()

def main():
    # Inicia la escucha
    try:
        channel.basic_consume(queue=queue_name, on_message_callback=callback)
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nShutting down worker...")
        connection.close()
    except Exception as global_error:
        print(f"Global worker error: {global_error}")
        if not connection.is_closed:
            connection.close()

if __name__ == "__main__":
    # 1. Start the health check server in a background thread
    # This prevents Hugging Face from timing out (30 min limit)
    health_thread = threading.Thread(target=run_health_check_server, daemon=True)
    health_thread.start()

    # 2. Start the RabbitMQ consumer
    print("[*] Starting document processor worker...")
    main()

