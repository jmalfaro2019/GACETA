# Congress Oversight - Colombian Legislative Monitoring System

An automated system for extracting, processing, and analyzing legislative documents from the Colombian Congress.

## Description

This project consists of four main components:

1. **Frontend** (Next.js/React): Web interface for viewing and querying laws and legislative projects.
2. **Gaceta Bot** (Scrapy): Web scraper for extracting legislative documents.
3. **Kafka Worker**: Document processor that converts PDF documents to Markdown format using OCR.
4. **ParadeDB** (PostgreSQL): Full-Text Search database engine to store and query the processed legislative text.

## System Requirements

- **Docker**: For running Kafka and ParadeDB (no local installations needed).
- **Docker Compose**: For orchestrating containers.
- **Python**: 3.10 (managed via Conda).
- **Node.js**: 18+ (for Frontend).
- **Git**: For version control.
- **DBeaver** (or similar SQL client): A graphical tool to visualize and manage the database.

---

## Project Setup

### Step 1: Start Infrastructure with Docker

Navigate to the `kafka/` folder and start the Kafka and ParadeDB containers:

```bash
cd kafka
docker-compose up -d
```

This will start:
- Apache Kafka broker (accessible at `localhost:9092`)
- Apache ZooKeeper (dependency for Kafka)
- **ParadeDB** (accessible at `localhost:5433`)

To verify the containers are running properly:

```bash
docker ps
```

### Step 2: Install and Configure DBeaver

To interact with the ParadeDB database, you need a database client. We recommend **DBeaver**.

1. **Download and Install:** Go to [dbeaver.io](https://dbeaver.io/) and download the free Community Edition for your operating system.
2. **Create a Connection:**
   - Open DBeaver and click on **New Database Connection** (the plug icon).
   - Select **PostgreSQL** as the database type.
3. **Enter Credentials:** Fill in the connection settings exactly as follows:
   - **Host:** `localhost`
   - **Port:** `5433` *(Note: We use 5433 to avoid conflicts with local Postgres installations)*
   - **Database:** `gaceta_db`
   - **Username:** `admin`
   - **Password:** `secret`
4. Click **Test Connection** (download drivers if prompted), then click **Finish**.

### Step 3: Initialize ParadeDB Schema

Before processing documents, you need to create the database table and the full-text search index.
In DBeaver, right-click on your new connection, open a **SQL Editor**, and execute the following script (using `Alt + X` or "Execute SQL Script"):

```sql
-- 1. Enable the ParadeDB search extension
CREATE EXTENSION IF NOT EXISTS pg_search;

-- 2. Create the documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(255),
    contenu_json TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create the BM25 full-text search index
CREATE INDEX recherche_documents_idx 
ON documents USING bm25 (id, titre, contenu_json) 
WITH (key_field='id');
```

### Step 4: Set Up Python Environment

Create and activate a Conda environment with Python 3.10:

```bash
# Create environment
conda create -n gaceta python=3.10 -y

# Activate environment
conda activate gaceta

# Install dependencies
pip install -r requirements.txt
```

*(Make sure `psycopg2-binary` is installed to allow Python to connect to ParadeDB).*

### Step 5: Configure Environment Variables

Create a `.env` file in the project root if needed:

```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
TOPIC=new_gazettes
GROUP_ID=pdf_processors_group_v4

GROQ_API_KEY="YOUR API KEY DE GROQ"
```

### Step 6: Start the Document Processor

Run the Kafka worker to process incoming documents. **Make sure to run this from the `kafka/` directory** so the script can resolve paths correctly:

```bash
cd kafka
python worker_procesador.py
```

The worker will:
- Listen for new documents on the Kafka topic `new_gazettes`.
- Convert PDF files to Markdown format using OCR models.
- Save processed files locally to `kafka/documents_markdown/`.
- **Insert the processed text and metadata directly into ParadeDB.**

### Step 7: Start the Scraper

In a new terminal (with the `gaceta` conda environment activated), run the Scrapy spider to download legislative documents:

```bash
cd gaceta_bot
scrapy crawl congreso
```

**How it works:**
- The spider downloads PDF documents from the Congress website.
- Saves them to `gaceta_bot/documents/`.
- Sends download notifications to Kafka.
- The worker immediately picks up the task, processes the PDF, and indexes it in the database.

### Step 8: Run the Frontend (Optional)

In a third terminal, start the web interface to query the processed laws:

```bash
cd Frontend
npm install
npm run dev
```

The web interface will be available at `http://localhost:3000`

---

## Stopping the Infrastructure

To stop Kafka and ParadeDB when finished:

```bash
cd kafka
docker-compose down
```

**⚠️ Warning:** To remove all containers AND permanently delete all stored database records:

```bash
cd kafka
docker-compose down -v
```

---

## Project Structure

```text
GACETA/
├── Frontend/                      # Next.js web interface (Connects to ParadeDB)
│   ├── app/                       # Application pages
│   ├── components/                # React components
│   └── data/                      # Static data
├── gaceta_bot/                    # Scrapy spider project
│   ├── documents/                 # Downloaded PDF documents
│   └── spiders/
│       └── congreso_spider.py     # Main scraper
├── kafka/                         # Infrastructure and Processing
│   ├── docker-compose.yml         # Kafka, Zookeeper, and ParadeDB setup
│   ├── worker_procesador.py       # PDF-to-Markdown + DB Ingestion script
│   └── documents_markdown/        # Local backups of processed Markdown files
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Troubleshooting

### Database Connection Refused

If the Python worker shows a `Connection refused` error on port 5433, ensure the `paradedb` container is running (`docker ps`) and that you have updated the port connection inside `worker_procesador.py` to `5433`.

### Kafka Connection Error

If you get `Failed to resolve KafkaProducerException`, ensure:
- Docker is running: `docker ps`
- Compose logs show no errors: `docker-compose logs`
- Port 9092 is accessible: `telnet localhost 9092`

### PDF Processing Errors

The worker supports GPU acceleration (CUDA) if available. Check logs for:
```text
NVIDIA GPU (CUDA) detected
```

### Python Package Issues

Clear and reinstall dependencies:

```bash
pip install --upgrade --force-reinstall -r requirements.txt
```

## Dependencies

See `requirements.txt` for detailed package versions.

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

**Database & Message Processing:**
- `confluent-kafka`: Kafka consumer for distributed document processing
- `psycopg2-binary`: PostgreSQL driver to connect the worker to ParadeDB

**Utilities:**
- `python-dotenv`: Environment variable management
- `python-json-logger`: JSON logging for debugging

## License

This project is open source.
