from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Header
import os
import json
import pika
from typing import List, Optional
from supabase import create_client, Client
from database import execute_query
from schemas import DocumentResponse, SearchResult
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

API_SECRET_KEY = os.getenv("API_SECRET_KEY", "super-secret-default-key")
RABBITMQ_URL = os.getenv("CLOUDAMQP_URL", "amqp://guest:guest@localhost/%2f")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(limit: int = 10, offset: int = 0):
    """Retrieves a list of analyzed documents from the database."""
    query = "SELECT * FROM documents ORDER BY date_creation DESC LIMIT %s OFFSET %s"
    results = execute_query(query, (limit, offset))
    if results is None:
        raise HTTPException(status_code=500, detail="Database error")
    return results

@router.get("/documents/search", response_model=List[SearchResult])
async def search_documents(q: str = Query(..., min_length=2)):
    """
    Performs a full-text search using standard PostgreSQL.
    Compatible with Supabase and other managed Postgres services.
    Searches across titles and the AI-generated AI summary.
    """
    # Standard PostgreSQL Full-Text Search logic
    search_query = """
        SELECT 
            id, 
            titre, 
            contenu_json->'metadatos_generales'->>'resumen_ia' as resumen_ia,
            contenu_json->'metadatos_generales'->>'tipo_documento' as tipo_documento,
            ts_rank_cd(
                to_tsvector('spanish', unaccent(titre) || ' ' || unaccent(COALESCE(contenu_json->'metadatos_generales'->>'resumen_ia', ''))),
                plainto_tsquery('spanish', unaccent(%s))
            ) as score
        FROM documents 
        WHERE to_tsvector('spanish', unaccent(titre) || ' ' || unaccent(COALESCE(contenu_json->'metadatos_generales'->>'resumen_ia', ''))) @@ plainto_tsquery('spanish', unaccent(%s))
        ORDER BY score DESC
        LIMIT 10;
    """
    
    results = execute_query(search_query, (q, q))
    
    if results is None:
        # Fallback to simple ILIKE search if FTS is not yet configured or for development
        fallback_query = """
            SELECT 
                id, titre, 
                contenu_json->'metadatos_generales'->>'resumen_ia' as resumen_ia,
                contenu_json->'metadatos_generales'->>'tipo_documento' as tipo_documento,
                1.0 as score
            FROM documents 
            WHERE titre ILIKE %s OR (contenu_json->'metadatos_generales'->>'resumen_ia') ILIKE %s
            LIMIT 10
        """
        results = execute_query(fallback_query, (f"%{q}%", f"%{q}%"))
        
    if results is None:
        raise HTTPException(status_code=500, detail="Search execution failed")
        
    return results

@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: int):
    """Retrieves a single document by its ID."""
    query = "SELECT * FROM documents WHERE id = %s"
    results = execute_query(query, (doc_id,))
    if not results:
        raise HTTPException(status_code=404, detail="Document not found")
    return results[0]

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    x_api_key: str = Header(None)
):
    """
    Securely uploads a PDF document to cloud storage and triggers the pipeline.
    """
    # 1. Security Check
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid API Key")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase Storage not configured")

    # 2. Upload to Supabase Storage
    try:
        content = await file.read()
        # Ensure filename is URL safe
        safe_filename = file.filename.replace(" ", "_")
        
        # Uploading to 'gazettes' bucket
        # We use upsert=True to allow retries
        res = supabase.storage.from_("gazettes").upload(
            path=safe_filename,
            file=content,
            file_options={"content-type": "application/pdf", "upsert": "true"}
        )
        
        # Get the public URL for the worker to download
        # Note: This assumes the 'gazettes' bucket is public. 
        # If private, you'd need a signed URL.
        public_url = supabase.storage.from_("gazettes").get_public_url(safe_filename)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloud Storage Error: {e}")

    # 3. Notify RabbitMQ (CloudAMQP)
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        queue_name = 'new_gazettes'
        channel.queue_declare(queue=queue_name, durable=True)
        
        # Prepare message for distributed worker
        # We send the public URL instead of a local path
        message = {
            "file": file.filename,
            "url": public_url,
            "status": "uploaded_to_cloud"
        }
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        return {"status": "success", "message": "File uploaded but notification failed", "url": public_url, "error": str(e)}

    return {"status": "success", "message": f"File uploaded and processing triggered", "url": public_url}
