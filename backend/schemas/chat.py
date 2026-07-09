from pydantic import BaseModel
from typing import List, Optional


class SourceItem(BaseModel):
    source_id: str
    title: str
    snippet: str
    distance: float


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    top_k: int = 4


class ChatResponse(BaseModel):
    answer: str
    route: str
    sources: List[SourceItem] = []