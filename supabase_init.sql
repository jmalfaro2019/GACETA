-- 1. Enable common extensions for document processing
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- 2. Create the documents table (Standard Postgres)
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    titre TEXT NOT NULL,
    contenu_json JSONB,
    date_creation TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create a Full-Text Search index (GIN)
-- This index will make searches across the title and the AI-generated summary extremely fast.
-- We use 'spanish' configuration and 'unaccent' to handle accents correctly.
CREATE INDEX IF NOT EXISTS documents_search_idx ON documents USING GIN (
    to_tsvector('spanish', unaccent(titre) || ' ' || unaccent(COALESCE(contenu_json->'metadatos_generales'->>'resumen_ia', '')))
);

-- 4. Create an optimized index for the JSONB structure (optional but recommended)
CREATE INDEX IF NOT EXISTS documents_json_idx ON documents USING GIN (contenu_json);

-- 5. Create a Storage Bucket for PDFs (Run this in the Supabase UI instead if preferred)
-- In Supabase, Buckets are usually managed via the Dashboard or API. 
-- Ensure you create a bucket named 'gazettes' and set it to Public or Private as needed.
