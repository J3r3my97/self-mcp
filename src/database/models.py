from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Category(BaseModel):
    id: str
    name: str
    parent_id: Optional[str] = None
    level: int = 1

class Attribute(BaseModel):
    id: str
    name: str
    type: str  # e.g., 'color', 'pattern', 'material'
    value: str

class Product(BaseModel):
    id: str
    brand: str
    name: str
    category_id: str
    price: float
    currency: str = "USD"
    source_url: str
    image_url: str
    attributes: List[Attribute] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DetectionResult(BaseModel):
    product_id: str
    similarity_score: float = Field(ge=0.0, le=1.0)
    bounding_box: Dict[str, float]  # x1, y1, x2, y2
    confidence: float = Field(ge=0.0, le=1.0)

class SearchResult(BaseModel):
    query_id: str
    results: List[DetectionResult]
    processing_time: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Firebase collection names
COLLECTIONS = {
    "products": "products",
    "categories": "categories",
    "attributes": "attributes",
    "searches": "searches"
}

# Firebase storage paths
STORAGE_PATHS = {
    "product_images": "product_images",
    "embeddings": "embeddings",
    "uploads": "uploads"
} 