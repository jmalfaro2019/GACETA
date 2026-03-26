# Congress Oversight - Colombian Legislative Monitoring System

An automated system for extracting, processing, and analyzing legislative documents from the Colombian Congress.

## Description

This project consists of three main components:

1. **Frontend** (Next.js/React): Web interface for viewing laws and legislative projects
2. **Gaceta Bot** (Scrapy): Web scraper for extracting legislative documents
3. **Kafka Worker**: PDF document processor converting to Markdown using AI

## Requirements

- Python 3.9+
- Node.js 18+
- Kafka (for distributed processing)
- Gemini API Key (for PDF processing)

## Installation

### Backend (Python)

```bash
pip install -r requirements.txt
```

### Frontend (Node.js)

```bash
cd Frontend
npm install
```

## Configuration

### Environment Variables

Create a `.env.local` file in the project root:

```env
GEMINI_API_KEY=your_gemini_key_here
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

## Usage

### Run the Scraper

```bash
cd gaceta_bot
scrapy crawl congreso
```

### Run the Kafka Document Processor

```bash
python kafka/worker_procesador.py
```

### Run the Frontend

```bash
cd Frontend
npm run dev
```

The application will be available at `http://localhost:3000`

## Project Structure

```
GACETA/
├── Frontend/           # Next.js application
├── gaceta_bot/         # Scrapy scraper
├── kafka/              # Document processor
└── README.md
```

## License

This project is open source.
