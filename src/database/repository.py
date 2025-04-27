import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from src.database.models import (
    COLLECTIONS,
    STORAGE_PATHS,
    Attribute,
    Category,
    DetectionResult,
    Product,
    SearchResult,
    User,
)
from src.utils.firebase_config import get_database, get_storage

# Configure logging
logger = logging.getLogger(__name__)


class FirebaseRepository:
    def __init__(self):
        self.db = get_database()
        self.storage = get_storage()

    # User operations
    async def create_user(self, user: User) -> str:
        """Create a new user in the database."""
        try:
            user_dict = user.model_dump()
            # Convert datetime objects to ISO format strings
            user_dict["created_at"] = user_dict["created_at"].isoformat()
            user_dict["updated_at"] = user_dict["updated_at"].isoformat()

            # Use Firebase Admin SDK reference syntax
            self.db.reference(f"{COLLECTIONS['users']}/{user.id}").set(user_dict)
            return user.id
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID from database."""
        try:
            user_data = self.db.reference(f"{COLLECTIONS['users']}/{user_id}").get()
            if not user_data:
                return None

            # Convert ISO format strings back to datetime objects
            user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
            user_data["updated_at"] = datetime.fromisoformat(user_data["updated_at"])

            return User(**user_data)
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None

    async def update_user(self, user_id: str, user: User) -> bool:
        """Update user in database."""
        try:
            user_dict = user.model_dump()
            user_dict["updated_at"] = user_dict["updated_at"].isoformat()
            self.db.reference(f"{COLLECTIONS['users']}/{user_id}").update(user_dict)
            return True
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return False

    # Product operations
    async def create_product(self, product: Product) -> str:
        """Create a new product in the database."""
        try:
            product_dict = product.model_dump()
            product_dict["created_at"] = product_dict["created_at"].isoformat()
            product_dict["updated_at"] = product_dict["updated_at"].isoformat()
            self.db.reference(f"{COLLECTIONS['products']}/{product.id}").set(product_dict)
            return product.id
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise

    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID from database."""
        try:
            product_data = self.db.reference(f"{COLLECTIONS['products']}/{product_id}").get()
            if not product_data:
                return None
            return Product(**product_data)
        except Exception as e:
            logger.error(f"Error getting product: {str(e)}")
            return None

    async def update_product(self, product_id: str, product: Product) -> bool:
        """Update product in database."""
        try:
            product_dict = product.model_dump()
            product_dict["updated_at"] = product_dict["updated_at"].isoformat()
            self.db.reference(f"{COLLECTIONS['products']}/{product_id}").update(product_dict)
            return True
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            return False

    # Category operations
    async def create_category(self, category: Category) -> str:
        """Create a new category in the database."""
        try:
            category_dict = category.model_dump()
            self.db.reference(f"{COLLECTIONS['categories']}/{category.id}").set(category_dict)
            return category.id
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            raise

    async def get_category(self, category_id: str) -> Optional[Category]:
        """Get category by ID from database."""
        try:
            category_data = self.db.reference(f"{COLLECTIONS['categories']}/{category_id}").get()
            if not category_data:
                return None
            return Category(**category_data)
        except Exception as e:
            logger.error(f"Error getting category: {str(e)}")
            return None

    # Search operations
    async def save_search_result(self, search_result: SearchResult) -> str:
        """Save search result to database."""
        try:
            search_dict = search_result.model_dump()
            search_dict["created_at"] = search_dict["created_at"].isoformat()
            self.db.reference(f"{COLLECTIONS['search_results']}/{search_result.id}").set(search_dict)
            return search_result.id
        except Exception as e:
            logger.error(f"Error saving search result: {str(e)}")
            raise

    # Storage operations
    async def upload_image(self, file_path: str, file_data: bytes) -> str:
        blob = self.storage.blob(f"{STORAGE_PATHS['uploads']}/{file_path}")
        blob.upload_from_string(file_data, content_type="image/jpeg")
        return blob.public_url

    async def upload_embedding(self, product_id: str, embedding: List[float]) -> str:
        """Upload product embedding to Firebase Storage."""
        try:
            # Convert embedding to bytes
            embedding_bytes = np.array(embedding).tobytes()

            # Upload to storage
            blob = self.storage.blob(f"{STORAGE_PATHS['embeddings']}/{product_id}.npy")
            blob.upload_from_string(embedding_bytes)

            return blob.public_url
        except Exception as e:
            logger.error(f"Error uploading embedding: {str(e)}")
            raise

    async def get_embedding(self, product_id: str) -> Optional[List[float]]:
        """Get product embedding from Firebase Storage."""
        try:
            # Get blob reference
            blob = self.storage.blob(f"{STORAGE_PATHS['embeddings']}/{product_id}.npy")

            # Check if embedding exists
            if not blob.exists():
                return None

            # Download embedding
            embedding_bytes = blob.download_as_bytes()
            embedding = np.frombuffer(embedding_bytes, dtype=np.float32).tolist()

            return embedding
        except Exception as e:
            logger.error(f"Error retrieving embedding: {str(e)}")
            return None

    async def get_search_result(self, query_id: str) -> Optional[SearchResult]:
        """Get search result by query ID from database."""
        try:
            search_data = self.db.reference(f"{COLLECTIONS['search_results']}/{query_id}").get()
            if not search_data:
                return None
            return SearchResult(**search_data)
        except Exception as e:
            logger.error(f"Error getting search result: {str(e)}")
            return None

    # Query operations
    async def search_products(self, query: Dict[str, Any], limit: int = 10) -> List[Product]:
        """Search products in database."""
        try:
            products_ref = self.db.reference(COLLECTIONS["products"])
            products_data = products_ref.get()
            if not products_data:
                return []

            products = []
            for product_id, product_data in products_data.items():
                if all(product_data.get(k) == v for k, v in query.items()):
                    products.append(Product(**product_data))
                    if len(products) >= limit:
                        break
            return products
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []

    async def check_connection(self) -> Dict[str, Any]:
        """Check database connection."""
        try:
            # Try to read a test value
            test_ref = self.db.reference("test")
            test_ref.set({"timestamp": datetime.now().isoformat()})
            test_data = test_ref.get()
            test_ref.delete()
            return {"status": "connected", "test_data": test_data}
        except Exception as e:
            return {"status": "disconnected", "error": str(e)}

    async def check_storage(self) -> Dict[str, Any]:
        """Check Firebase Storage status."""
        try:
            # Try to list files in a test directory
            bucket = self.storage.bucket()
            blobs = bucket.list_blobs(prefix="test/", max_results=1)
            list(blobs)  # Force evaluation
            return {
                "status": "healthy",
                "details": {"bucket_name": bucket.name, "connected": True},
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
