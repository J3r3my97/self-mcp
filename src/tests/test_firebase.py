import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import uuid

from src.database.models import Category, Product
from src.database.repository import FirebaseRepository
from src.utils.firebase_config import (get_database, get_storage,
                                       initialize_firebase)


def test_firebase_connection():
    print("Testing Firebase connection...")

    # Initialize Firebase
    if not initialize_firebase():
        print("Failed to initialize Firebase")
        return False

    print("Firebase initialized successfully")
    return True


async def test_database_operations():
    print("\nTesting database operations...")
    repo = FirebaseRepository()

    # Test creating a category
    category = Category(id=str(uuid.uuid4()), name="Test Category", level=1)

    try:
        category_id = await repo.create_category(category)
        print(f"Created category with ID: {category_id}")

        # Test creating a product
        product = Product(
            id=str(uuid.uuid4()),
            brand="Test Brand",
            name="Test Product",
            category_id=category_id,
            price=99.99,
            currency="USD",
            source_url="https://example.com",
            image_url="https://example.com/image.jpg",
        )

        product_id = await repo.create_product(product)
        print(f"Created product with ID: {product_id}")

        # Test retrieving the product
        retrieved_product = await repo.get_product(product_id)
        if retrieved_product:
            print(f"Retrieved product: {retrieved_product.name}")
        else:
            print("Failed to retrieve product")

        return True
    except Exception as e:
        print(f"Error during database operations: {e}")
        return False


async def test_storage_operations():
    print("\nTesting storage operations...")
    repo = FirebaseRepository()

    try:
        # Test uploading a small text file
        test_content = b"Hello, Firebase Storage!"
        file_path = "test/test.txt"

        url = await repo.upload_image(file_path, test_content)
        print(f"Uploaded file to: {url}")
        return True
    except Exception as e:
        print(f"Error during storage operations: {e}")
        return False


async def main():
    print("Starting Firebase integration tests...")

    # Test Firebase connection
    if not test_firebase_connection():
        return

    # Test database operations
    if not await test_database_operations():
        return

    # Test storage operations
    if not await test_storage_operations():
        return

    print("\nAll tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
