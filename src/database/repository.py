import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..utils.firebase_config import get_database, get_storage
from .models import (
    COLLECTIONS,
    STORAGE_PATHS,
    Attribute,
    Category,
    DetectionResult,
    Product,
    SearchResult,
)


class FirebaseRepository:
    def __init__(self):
        self.db = get_database()
        self.storage = get_storage()

    # Product operations
    async def create_product(self, product: Product) -> str:
        product_id = str(uuid.uuid4())
        product_dict = product.model_dump()
        product_dict['id'] = product_id
        
        # Convert datetime objects to ISO format strings
        product_dict['created_at'] = product_dict['created_at'].isoformat()
        product_dict['updated_at'] = product_dict['updated_at'].isoformat()
        
        self.db.child(COLLECTIONS['products']).child(product_id).set(product_dict)
        return product_id

    async def get_product(self, product_id: str) -> Optional[Product]:
        product_data = self.db.child(COLLECTIONS['products']).child(product_id).get()
        if not product_data:
            return None
            
        # Convert ISO format strings back to datetime objects
        product_data['created_at'] = datetime.fromisoformat(product_data['created_at'])
        product_data['updated_at'] = datetime.fromisoformat(product_data['updated_at'])
        
        return Product(**product_data)

    async def update_product(self, product_id: str, product: Product) -> bool:
        try:
            product_dict = product.model_dump()
            # Convert datetime objects to ISO format strings
            product_dict['created_at'] = product_dict['created_at'].isoformat()
            product_dict['updated_at'] = product_dict['updated_at'].isoformat()
            
            self.db.child(COLLECTIONS['products']).child(product_id).update(product_dict)
            return True
        except Exception:
            return False

    # Category operations
    async def create_category(self, category: Category) -> str:
        category_id = str(uuid.uuid4())
        category_dict = category.model_dump()
        category_dict['id'] = category_id
        self.db.child(COLLECTIONS['categories']).child(category_id).set(category_dict)
        return category_id

    async def get_category(self, category_id: str) -> Optional[Category]:
        category_data = self.db.child(COLLECTIONS['categories']).child(category_id).get()
        return Category(**category_data) if category_data else None

    # Search operations
    async def save_search_result(self, search_result: SearchResult) -> str:
        search_id = str(uuid.uuid4())
        search_dict = search_result.model_dump()
        search_dict['query_id'] = search_id
        search_dict['created_at'] = search_dict['created_at'].isoformat()
        
        self.db.child(COLLECTIONS['searches']).child(search_id).set(search_dict)
        return search_id

    # Storage operations
    async def upload_image(self, file_path: str, file_data: bytes) -> str:
        blob = self.storage.blob(f"{STORAGE_PATHS['uploads']}/{file_path}")
        blob.upload_from_string(file_data, content_type='image/jpeg')
        return blob.public_url

    async def upload_embedding(self, product_id: str, embedding: List[float]) -> str:
        blob = self.storage.blob(f"{STORAGE_PATHS['embeddings']}/{product_id}.npy")
        blob.upload_from_string(str(embedding))
        return blob.public_url

    # Query operations
    async def search_products(self, query: Dict[str, Any], limit: int = 10) -> List[Product]:
        # Basic search implementation - will be enhanced with vector search
        products_ref = self.db.child(COLLECTIONS['products'])
        results = []
        
        # Simple attribute matching for MVP
        for product_data in products_ref.get().values():
            # Convert ISO format strings back to datetime objects
            product_data['created_at'] = datetime.fromisoformat(product_data['created_at'])
            product_data['updated_at'] = datetime.fromisoformat(product_data['updated_at'])
            
            product = Product(**product_data)
            if all(getattr(product, k) == v for k, v in query.items()):
                results.append(product)
                if len(results) >= limit:
                    break
        
        return results 