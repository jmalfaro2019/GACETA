# Congress Oversight - Colombian Legislative Monitoring System

An automated system for extracting, processing, and analyzing legislative documents from the Colombian Congress.

## Description

This project consists of three main components:

1. **Frontend** (Next.js/React): Web interface for viewing laws and legislative projects
2. **Gaceta Bot** (Scrapy): Web scraper for extracting legislative documents
3. **Kafka Worker**: Document processor that converts PDF documents to Markdown format

## System Requirements

- **Python**: 3.10 (managed via Conda)
- **Node.js**: 18+ (for Frontend)
- **Kafka**: Latest version (for message streaming)
- **Git**: For version control

## Project Setup

### Step 1: Configure Kafka

Download and extract Apache Kafka, then follow the detailed setup instructions:

👉 **See [gaceta_bot/kafka/instrucciones.txt](gaceta_bot/kafka/instrucciones.txt) for complete Kafka setup commands**

In summary:
1. Format the Kafka cluster (first time only)
2. Start the Kafka server
3. Create the `gacetas_nuevas` topic
4. (Optional) Start a producer/consumer for testing

### Step 2: Set Up Python Environment

Create and activate a Conda environment with Python 3.10:

```bash
# Create environment
conda create -n gaceta python=3.10 -y

# Activate environment
conda activate gaceta

# Install dependencies
pip install -r requirements.txt
```

### Step 3: (Optional) Verify Kafka Connection

Run a Kafka consumer to verify the producer is sending messages correctly:

```bash
<kafka-installation-directory>\bin\windows\kafka-console-consumer.bat --topic gacetas_nuevas --from-beginning --bootstrap-server localhost:9092
```

### Step 4: Start the Document Processor

Run the Kafka worker to process incoming documents:

```bash
python kafka/worker_procesador.py
```

### Step 5: Start the Scraper

Run the Scrapy spider to download legislative documents:

```bash
cd gaceta_bot
scrapy crawl congreso
```

**How it works:**
- The spider downloads PDF documents and saves them to `gaceta_bot/documents/`
- The Kafka worker monitors for new documents and converts them to Markdown format
- Processed documents are saved to `kafka/documents_markdown/`

### Step 6: Run the Frontend (Optional)

```bash
cd Frontend
npm install
npm run dev
```

The web interface will be available at `http://localhost:3000`

## Project Structure

```
GACETA/
├── Frontend/                  # Next.js web interface
├── gaceta_bot/
│   ├── documents/            # Downloaded PDF documents
│   ├── spiders/
│   │   └── congreso_spider.py # Scrapy spider
│   └── kafka/
│       └── instrucciones.txt  # Kafka setup commands
├── kafka/
│   ├── worker_procesador.py  # Document processor
│   └── documents_markdown/    # Processed Markdown files
└── requirements.txt           # Python dependencies
```

## Dependencies

See [requirements.txt](requirements.txt) for detailed package versions.

### Key Libraries

**Data Collection:**
- `scrapy`: Web scraping framework for downloading legislative documents
- `requests`: HTTP requests library

**PDF Processing & OCR:**
- `pdfplumber`: Advanced table and structured data extraction from PDFs
- `PyMuPDF` (fitz): Fast PDF parsing and content extraction
- `easyocr`: Optical Character Recognition (OCR) for text in images and scanned documents
- `torch` & `torchvision`: Deep learning libraries that power EasyOCR
- `numpy`: Numerical computing library
- `Pillow`: Image processing library

**Message Processing:**
- `confluent-kafka`: Kafka consumer for distributed document processing

**Utilities:**
- `python-dotenv`: Environment variable management
- `python-json-logger`: JSON logging for debugging

## License

This project is open source.
