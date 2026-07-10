from pydantic import BaseModel
from typing import List, Optional
from backend.core.config import DEFAULT_TOP_K


class SourceItem(BaseModel):
    source_id: str
    title: str
    snippet: str
    distance: float


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    top_k: int = DEFAULT_TOP_K


class ChatResponse(BaseModel):
    answer: str
    route: str
    sources: List[SourceItem] = []