import json
import os
from dotenv import load_dotenv
from confluent_kafka import Consumer
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.output import text_from_rendered

# 1. Your Gemini API Key (Replace with yours!)
# This allows Marker to use AI in the cloud to read images and tables
load_dotenv()
api_key_gemini = os.getenv('API_KEY')
os.environ["GEMINI_API_KEY"] = api_key_gemini

# 2. Marker Configuration
config = {
    "output_format": "markdown",
    "use_llm": True, # Enable AI usage for tables/images
    "llm_service": "marker.services.gemini.GoogleGeminiService" # Use Gemini
}
config_parser = ConfigParser(config)

# 3. Initialize the converter
print("Loading Marker model (this is fast)...")
converter = PdfConverter(
    config=config_parser.generate_config_dict(),
    artifact_dict=create_model_dict(),
    processor_list=config_parser.get_processors(),
    renderer=config_parser.get_renderer(),
    llm_service=config_parser.get_llm_service()
)

# 4. Configure Kafka
kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'marker_processors_group_v1', 
    'auto.offset.reset': 'latest'
}

consumer = Consumer(kafka_config)
consumer.subscribe(['new_gazettes'])

# Create results folder
os.makedirs("documents_markdown", exist_ok=True)
print("✓ Marker Worker ready! Waiting for PDFs...\n")

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
        file_name_only = os.path.basename(data['file']) 
        base_name = file_name_only.replace('.pdf', '')
        
        # Real path to the PDF
        real_pdf_path = os.path.normpath(os.path.join("..", "gaceta_bot", original_pdf_path))
        
        print(f"📥 Processing with Marker: {file_name_only}")

        try:
            # 5. Conversion with Marker
            rendered = converter(real_pdf_path)
            markdown_text, _, images = text_from_rendered(rendered)
            
            # Save the Markdown
            md_path = os.path.normpath(os.path.join("documents_markdown", f"{base_name}.md"))
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(markdown_text)
                
            # Optional: Save extracted images
            if images:
                print(f"   📸 Found {len(images)} images. (You can configure to save them).")
                
            print(f"✅ Success! Saved at: {md_path}\n")
            
        except Exception as e:
            print(f"❌ Error converting: {e}\n")

except KeyboardInterrupt:
    print("Shutting down Worker...")
finally:
    consumer.close()