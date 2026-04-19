import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_CONFIG = {
    "dbname": "gaceta_db",
    "user": "admin",
    "password": "secret",
    "host": "localhost",
    "port": "5433"
}

def get_db_connection():
    """Returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def execute_query(query: str, params: tuple = None, fetch: bool = True):
    """Executes a raw SQL query and returns results as dictionaries."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        # Use RealDictCursor to return results as dictionaries (easier for JSON response)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch:
                result = cur.fetchall()
            else:
                conn.commit()
                result = True
        return result
    except Exception as e:
        print(f"Database query error: {e}")
        return None
    finally:
        conn.close()
