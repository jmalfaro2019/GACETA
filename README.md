# Congress Oversight - Colombian Legislative Monitoring System

An automated system for extracting, processing, and analyzing legislative documents from the Colombian Congress.

## Description

This project consists of four main compoVnents:

1. **Frontend** (Next.js/React): Web interface for monitorinig. Hosted on **Vercel**.
2. **REST API** (FastAPI): Centralized backend for search and ingestion. Hosted on **Koyeb**.
3. **Supabase Storage/DB**: Stores processed documents and handles Full-Text Search.
4. **Hugging Face Worker**: Background worker for OCR and AI. Hosted on **HF Spaces** (Docker).
5. **RabbitMQ**: Cloud communication via **CloudAMQP**.

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

Navigate to the `kafka/` folder and start the infrastructure. *Note: We are using CloudAMQP for RabbitMQ, so Docker is primarily for ParadeDB:*

```bash
cd kafka
docker-compose up -d
```

This will start:
- **ParadeDB** (accessible at `localhost:5433`)
- The internal networking for future services.

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
-- 1. Habilitar la extensión de búsqueda de ParadeDB
CREATE EXTENSION IF NOT EXISTS pg_search;

-- 2. Crear la tabla de documentos (ajustada a JSONB)
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(255) NOT NULL,
    contenu_json JSONB, -- Cambiado de TEXT a JSONB
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Crear el índice de búsqueda BM25
-- ParadeDB indexará automáticamente el texto dentro del JSONB
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

Create a `.env` file in the project root:

```bash
# Infrastructure
CLOUDAMQP_URL="amqps://your-cloudamqp-url"

# AI Analysis
GROQ_API_KEY="YOUR_GROQ_API_KEY"

# Frontend
NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"
```

### Step 6: Start the Document Processor

Run the worker to process incoming documents from RabbitMQ:

```bash
cd kafka
python worker_procesador.py
```

The worker now follows a **3-Stage Modular Pipeline**:
1. **Extraction (PDF -> MD)**: Converts PDF to Markdown and **saves a checkpoint** to `documents_markdown/`.
2. **Analysis (MD -> JSON)**: Uses Groq AI to analyze the markdown and generate structured metadata.
3. **Ingestion (JSON -> DB)**: Automatically inserts the results into ParadeDB.

> [!TIP]
> If the AI stage fails (e.g. rate limits), the Markdown checkpoint is preserved on disk, allowing you to resume later.

### Step 7: Start the Scraper

In a new terminal (with the `gaceta` conda environment activated), run the Scrapy spider to download legislative documents:

```bash
cd gaceta_bot
scrapy crawl congreso
```

**How it works:**
- The spider downloads PDF documents from the Congress website.
- Saves them locally to `gaceta_bot/documents/`.
- Sends download notifications to **RabbitMQ (CloudAMQP)**.
- The worker immediately picks up the task, processes the PDF, and indexes it in the database.

### Step 8: Start the REST API

The frontend now communicates with a dedicated backend service for faster search and data validation:

```bash
# From the project root
uvicorn backend.main:app --reload
```
- **Swagger Docs:** `http://localhost:8000/docs`
- **Port:** 8000

### Step 9: Run the Frontend

Start the web interface:

```bash
cd Frontend
npm install
npm run dev
```

The web interface will be available at `http://localhost:3000`

---

## Operations & Utilities

### Mass Ingestion (Batch Parser)
If you have a large mass of existing Markdown files, you can skip the PDF extraction and run the AI analysis/ingestion in bulk:

```bash
cd kafka
python batch_parser.py
```
This script features **checkpointing**: it will automatically skip any file that has already been successfully analyzed and inserted into the database.

## Stopping the Infrastructure

To stop ParadeDB:

```bash
cd kafka
docker-compose down
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

## Cloud Deployment Guide

This project is designed to be deployed across several free-tier cloud providers for a fully autonomous monitoring system.

### 1. Database & Storage (Supabase)
1. Create a project on [Supabase](https://supabase.com/).
2. Run the [supabase_init.sql](file:///c:/Users/alfar/OneDrive/Escritorio/PROYECTOS/GACETA/supabase_init.sql) script in the SQL Editor.
3. Create a **Storage Bucket** named `gazettes` and set its policy to "Public" (or update the code for signed URLs).

### 2. Message Broker (CloudAMQP)
1. Create a free instance on [CloudAMQP](https://www.cloudamqp.com/).
2. Copy the **AMQP URL**.

### 3. Backend API (Koyeb)
1. Point Koyeb to your GitHub repository.
2. Select the `/backend` folder or use the root with the `backend/Dockerfile`.
3. Set the Environment Variables: `SUPABASE_URL`, `SUPABASE_KEY`, `CLOUDAMQP_URL`, `API_SECRET_KEY`.

### 4. Processing Worker (Hugging Face Spaces)
1. Create a new **Docker Space** on Hugging Face.
2. Set it to **Public**.
3. Upload the contents of the `kafka/` directory (including its Dockerfile and README).
4. Configured the Secrets: `CLOUDAMQP_URL`, `SUPABASE_URL`, `SUPABASE_KEY`, `GROQ_API_KEY`.

### 5. Frontend (Vercel)
1. Import the repository in Vercel.
2. Set `NEXT_PUBLIC_API_URL` to your Koyeb API URL.

---

## License

This project is open source.
