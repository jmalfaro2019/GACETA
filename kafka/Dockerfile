# Use Python 3.10 as base
FROM python:3.10

# Install system dependencies for OCR (EasyOCR needs these for cv2 and glib)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy ONLY the worker requirements first for caching
COPY kafka/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download EasyOCR models so they are ready at runtime
RUN python -c "import easyocr; easyocr.Reader(['es'])"

# Copy the worker code
COPY kafka/ .

# HF Spaces requires a port to be exposed (usually 7860) 
EXPOSE 7860

# Command to run the worker
# We assume worker_procesador.py is in the root of /app
CMD ["python", "worker_procesador.py"]
