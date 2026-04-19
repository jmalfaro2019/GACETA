import os
import json
import sys
import psycopg2
from groq_parser import parse_markdown_to_json

# --- CONFIGURATION ---
INPUT_DIR = "documents_markdown"
OUTPUT_DIR = "documents_json"
DB_CONFIG = {
    "dbname": "gaceta_db",
    "user": "admin",
    "password": "secret",
    "host": "localhost",
    "port": "5433"
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def process_batch():
    # Ensure directories exist
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Input directory '{INPUT_DIR}' not found.")
        return
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Scan for all markdown files
    md_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".md")]
    md_files.sort() # Process in alphabetical order for consistency

    if not md_files:
        print("No markdown files found to process.")
        return

    print(f"Found {len(md_files)} files in '{INPUT_DIR}'.")

    # 2. Process each file
    for index, filename in enumerate(md_files):
        base_name = filename.replace(".md", "")
        json_path = os.path.join(OUTPUT_DIR, f"{base_name}.json")

        # Checkpoint: Skip if JSON already exists
        if os.path.exists(json_path):
            print(f"[{index+1}/{len(md_files)}] Skipping '{filename}' (Already processed).")
            continue

        print(f"[{index+1}/{len(md_files)}] Processing '{filename}'...")
        
        md_path = os.path.join(INPUT_DIR, filename)
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                markdown_text = f.read()
        except Exception as e:
            print(f"Error reading file '{filename}': {e}")
            continue

        # --- AI PARSING ---
        try:
            structured_data = parse_markdown_to_json(markdown_text)
        except Exception as ai_error:
            print(f"FATAL ERROR during AI parsing of '{filename}': {ai_error}")
            print("Stopping batch process to save resources.")
            sys.exit(1)

        # --- SAVE JSON ---
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(structured_data, f, ensure_ascii=False, indent=4)
            print(f"  - Saved JSON to '{json_path}'")
        except Exception as e:
            print(f"  - Error saving JSON for '{filename}': {e}")
            continue

        # --- DATABASE INSERTION ---
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                ai_title = structured_data.get("metadatos_generales", {}).get("titulo_principal", base_name)
                json_str = json.dumps(structured_data)

                insert_query = """
                    INSERT INTO documents (titre, contenu_json)
                    VALUES (%s, %s);
                """
                cursor.execute(insert_query, (ai_title, json_str))
                conn.commit()
                cursor.close()
                conn.close()
                print(f"  - Successfully inserted into DB: '{ai_title}'")
            except Exception as db_error:
                print(f"  - DB Error for '{filename}': {db_error}")
                if conn: conn.close()
        else:
            print(f"  - Warning: Skipping DB insertion for '{filename}' due to connection failure.")

    print("\n--- Batch processing complete! ---")

if __name__ == "__main__":
    process_batch()
