from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


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


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class ProductResponse(BaseModel):
    id: str
    brand: str
    name: str
    price: float
    currency: str
    source_url: str
    image_url: str


class DetectionResponse(BaseModel):
    product: Optional[ProductResponse] = None
    similarity_score: float = Field(ge=0.0, le=1.0)
    bounding_box: BoundingBox
    confidence: float = Field(ge=0.0, le=1.0)


class SearchResponse(BaseModel):
    query_id: str
    results: List[DetectionResponse]
    processing_time: float
    created_at: datetime


class ComponentStatus(BaseModel):
    status: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    components: Dict[str, ComponentStatus]
    timestamp: float
    error: Optional[str] = None
