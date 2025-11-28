from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ArticleDTO(BaseModel):
    """Data Transfer Object for an Article"""
    id: int
    title: str
    summary: Optional[str] = None
    url: str
    source: str
    category: Optional[str] = "Other"
    published_at: Optional[str] = None

class SearchResponse(BaseModel):
    """Response model for search results"""
    count: int
    results: List[ArticleDTO]

class IngestResponse(BaseModel):
    status: str
    message: str
    articles_processed: int