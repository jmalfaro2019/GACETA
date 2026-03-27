import json
import os
from confluent_kafka import Consumer
import easyocr
import numpy as np
import torch
import fitz  # For columns and images
import pdfplumber  # The table expert
import io
from PIL import Image

# --- AUTOMATIC HARDWARE DETECTION ---
if torch.cuda.is_available():
    print("🚀 NVIDIA GPU (CUDA) detected!")
    use_gpu = True
else:
    print("💻 Using CPU")
    use_gpu = False

print("Loading EasyOCR model...")
reader = easyocr.Reader(['es', 'en'], gpu=use_gpu)

# Kafka configuration
kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'pdf_processors_group_v4',
    'auto.offset.reset': 'latest'
}

consumer = Consumer(kafka_config)
consumer.subscribe(['new_gazettes'])

os.makedirs("documents_markdown", exist_ok=True)
print("✓ Master hybrid worker (PDFPlumber + PyMuPDF + EasyOCR) ready!\n")

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
        print(f"\n  📄 Starting page {page_num + 1}...")
        page_content = []
        page_fitz = doc_fitz[page_num]
        page_plumb = pdf_plumb.pages[page_num]
        
        table_bboxes = []
        
        # 1. TABLES
        print(f"    ⏳ Searching for tables...")
        tables = page_plumb.find_tables()
        for i, table in enumerate(tables):
            table_bboxes.append(table.bbox)
            table_data = table.extract()
            md_table = table_to_markdown(table_data)
            page_content.append(f"\n> **Table {i+1} detected:**\n\n{md_table}")
        print(f"    ✅ Tables ready ({len(tables)} found).")

        # 2. IMAGES
        print(f"    ⏳ Extracting and reading images...")
        image_list = page_fitz.get_images(full=True)
        for i, img in enumerate(image_list):
            xref = img[0]
            try:
                base_image = doc_fitz.extract_image(xref)
                image_bytes = base_image["image"]
                
                image = Image.open(io.BytesIO(image_bytes))
                
                # --- NEW: SIZE FILTER ---
                width, height = image.size
                if width < 50 or height < 50:
                    print(f"      ⏭️ Image {i+1} skipped (too small: {width}x{height})")
                    continue  # Ignore noise and logos
                
                # Resize very large images to avoid memory issues
                if width > 2000 or height > 2000:
                    image.thumbnail((2000, 2000))
                # ------------------------

                if image.mode != 'RGB':
                    image = image.convert('RGB')
                img_array = np.array(image)
                
                print(f"      👁️ Applying OCR to image {i+1} ({image.size})...")
                ocr_results = reader.readtext(img_array, detail=0)
                ocr_text = "\n".join(ocr_results)
                
                if ocr_text.strip():
                    page_content.append(f"\n> *Text from image {i+1}:*\n> {ocr_text}\n")
            except Exception as e:
                print(f"      ⚠️ Image warning on page {page_num + 1}: {e}")
        print(f"    ✅ Images ready.")

        # 3. TEXT
        print(f"    ⏳ Extracting normal text...")
        # ... (The same block-processing code you already have continues here) ...
        
        print(f"    ✅ Text ready.")

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
        
        print(f"📥 Processing: {file_name_only}")

        try:
            markdown_text = process_pdf_master(real_pdf_path)
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