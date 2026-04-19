# Use Python 3.10 as base
FROM python:3.10

# Install system dependencies for OCR (EasyOCR needs these for cv2 and glib)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements from the root and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the worker code and its local dependencies
COPY kafka/ ./kafka/

# HF Spaces requires a port to be exposed (usually 7860) 
# even if we are only running a background consumer.
EXPOSE 7860

# Command to run the worker
# We use the relative path to the script
CMD ["python", "kafka/worker_procesador.py"]
