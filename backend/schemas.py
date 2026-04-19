from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class DocumentBase(BaseModel):
    titre: str
    contenu_json: Any
    date_creation: datetime

class DocumentResponse(DocumentBase):
    id: int

class SearchResult(BaseModel):
    id: int
    titre: str
    resumen_ia: Optional[str] = None
    tipo_documento: Optional[str] = None
    score: float # ParadeDB relevance score
