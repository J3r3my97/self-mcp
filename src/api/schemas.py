from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class FashionItem(BaseModel):
    category: str
    brand: str
    name: str
    price: float
    url: str
    similarity_score: float = Field(ge=0.0, le=1.0)
    
    class Config:
        from_attributes = True

class DetectionResult(BaseModel):
    items: List[FashionItem]
    processing_time: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    detail: str
    code: str
    timestamp: datetime = Field(default_factory=datetime.utcnow) 