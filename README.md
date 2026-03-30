# Congress Oversight - Colombian Legislative Monitoring System

An automated system for extracting, processing, and analyzing legislative documents from the Colombian Congress.

## Description

This project consists of three main components:

1. **Frontend** (Next.js/React): Web interface for viewing laws and legislative projects
2. **Gaceta Bot** (Scrapy): Web scraper for extracting legislative documents
3. **Kafka Worker**: Document processor that converts PDF documents to Markdown format

## System Requirements

- **Docker**: For running Kafka (no local Kafka installation needed)
- **Docker Compose**: For orchestrating containers
- **Python**: 3.10 (managed via Conda)
- **Node.js**: 18+ (for Frontend)
- **Git**: For version control

## Project Setup

### Step 1: Start Kafka with Docker

Navigate to the `kafka/` folder and start the Kafka containers:

```bash
cd kafka
docker-compose up -d
```

This will start:
- Apache Kafka broker (accessible at `localhost:9092`)
- Apache ZooKeeper (dependency for Kafka)

To verify Kafka is running:

```bash
docker ps
```

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

### Step 3: Configure Environment Variables

Create a `.env` file in the project root if needed:

```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
TOPIC=new_gazettes
GROUP_ID=pdf_processors_group_v4
```

### Step 4: Start the Document Processor

Run the Kafka worker to process incoming documents:

```bash
python kafka/worker_procesador.py
```

The worker will:
- Listen for new documents on the Kafka topic
- Convert PDF files to Markdown format
- Save processed files to `kafka/documents_markdown/`

### Step 5: Start the Scraper

In a new terminal, run the Scrapy spider to download legislative documents:

```bash
cd gaceta_bot
scrapy crawl congreso
```

**How it works:**
- The spider downloads PDF documents from the Congress website
- Saves them to `gaceta_bot/documents/`
- Sends download notifications to Kafka
- The worker processes each document and converts it to Markdown

### Step 6: Run the Frontend (Optional)

```bash
cd Frontend
npm install
npm run dev
```

The web interface will be available at `http://localhost:3000`

## Stopping Kafka

To stop Kafka when finished:

```bash
cd kafka
docker-compose down
```

To remove all data and restart fresh:

```bash
cd kafka
docker-compose down -v
```

## Project Structure

```
GACETA/
├── Frontend/                      # Next.js web interface
│   ├── app/                      # Application pages
│   ├── components/               # React components
│   └── data/                     # Static data
├── gaceta_bot/                   # Scrapy spider project
│   ├── documents/                # Downloaded PDF documents
│   ├── spiders/
│   │   └── congreso_spider.py   # Main scraper
│   └── gaceta_bot/
│       ├── settings.py           # Scrapy configuration
│       ├── items.py              # Data models
│       ├── pipelines.py          # Processing pipelines
│       └── middlewares.py        # Spider middlewares
├── kafka/                        # Kafka worker and Docker setup
│   ├── docker-compose.yml        # Docker Compose configuration
│   ├── worker_procesador.py      # PDF-to-Markdown converter
│   └── documents_markdown/       # Processed Markdown files
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Troubleshooting

### Kafka Connection Error

If you get `Failed to resolve KafkaProducerException`, ensure:
- Docker is running: `docker ps`
- Compose logs show no errors: `docker-compose logs`
- Port 9092 is accessible: `telnet localhost 9092`

### PDF Processing Errors

The worker supports GPU acceleration (CUDA) if available. Check logs for:
```
NVIDIA GPU (CUDA) detected
```

### Python Package Issues

Clear and reinstall dependencies:
```bash
pip install --upgrade --force-reinstall -r requirements.txt
```

## Notes

- OCR processing may take time depending on document size and available hardware
- The spider respects the website's robots.txt and applies rate limiting
- All environment variables can be configured via system variables or `.env` file
│   ├── worker_procesador.py  # Document processor
│   └── documents_markdown/    # Processed Markdown files
└── requirements.txt           # Python dependencies

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
