# Use an official Python slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2 and other tools
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only the backend dependencies first (for better caching)
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
# This copies the CONTENT of the backend/ directory to /app
COPY backend/ .

# Expose the API port
EXPOSE 8000

# Command to run the FastAPI app
# We use 'main:app' because main.py is now in the root of /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
