from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# HOTFIX: Render sometimes sets HTTP_PROXY which breaks the Supabase client
# with a "unexpected keyword argument 'proxy'" error.
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

from routes import documents

app = FastAPI(
    title="GACETA AI API",
    description="REST API for the Colombian Congress Document Analysis System",
    version="1.0.0"
)

# Configure CORS
# In production, change "*" to the specific URL of your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include generic routes
app.include_router(documents.router, prefix="/api/v1", tags=["Documents"])

@app.get("/")
async def health_check():
    return {
        "status": "online",
        "system": "GACETA AI",
        "version": "1.0.0"
    }
