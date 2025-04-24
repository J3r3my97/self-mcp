import asyncio
import io
import logging
import os
from datetime import datetime
from pathlib import Path

import firebase_admin
import numpy as np
import pytest
import torch
from firebase_admin import credentials
from PIL import Image

from src.database.models import SearchResult
from src.database.repository import FirebaseRepository
from src.models.fashion_detector import FashionDetector
from src.models.similarity_search import SimilaritySearch
from src.services.image_processor import ImageProcessor
from src.utils.firebase_config import initialize_firebase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data paths
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_IMAGE_PATH = TEST_DATA_DIR / "test_image.jpg"

@pytest.fixture(scope="session", autouse=True)
def setup_firebase():
    """Initialize Firebase for testing."""
    try:
        # Initialize Firebase
        initialize_firebase()
    except ValueError as e:
        if "already exists" not in str(e):
            raise

@pytest.fixture
def repository():
    return FirebaseRepository()

@pytest.fixture
def sample_image():
    # Create a simple test image
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    # Add some simple shapes to make it more realistic
    img[50:150, 50:150] = 255  # White square
    return Image.fromarray(img)

@pytest.fixture
def fashion_detector():
    return FashionDetector(device='cpu')

@pytest.fixture
def similarity_search(repository):
    return SimilaritySearch(repository)

@pytest.fixture
def image_processor(fashion_detector, similarity_search, repository):
    return ImageProcessor(fashion_detector, similarity_search, repository)

@pytest.fixture
def test_image():
    """Create a test image."""
    # Create a test image (RGB format)
    test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    image = Image.fromarray(test_image, mode='RGB')
    
    # Save the image
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    image.save(TEST_IMAGE_PATH, format='JPEG')
    
    return image

@pytest.mark.asyncio
async def test_fashion_detector(fashion_detector, sample_image):
    """Test FashionDetector functionality."""
    # Convert PIL Image to numpy array
    img_array = np.array(sample_image)
    
    # Test detection
    detections = fashion_detector.forward(img_array)
    assert isinstance(detections, list)
    
    if detections:  # If any detections found
        detection = detections[0]
        assert 'box' in detection
        assert 'confidence' in detection
    
    # Test embedding extraction
    embeddings = fashion_detector.get_embeddings(img_array)
    assert isinstance(embeddings, list)
    assert len(embeddings) == 768  # ViT base model output dimension

@pytest.mark.asyncio
async def test_similarity_search(similarity_search):
    """Test SimilaritySearch functionality."""
    # Create random embeddings for testing
    query_embedding = np.random.rand(768).tolist()
    
    # Test search functionality
    results = await similarity_search.search(query_embedding, top_k=5)
    assert isinstance(results, list)
    if results:  # If any results found
        assert all(0 <= result['similarity'] <= 1 for result in results)
        assert len(results) <= 5

@pytest.mark.asyncio
async def test_image_processor(image_processor, sample_image):
    """Test ImageProcessor functionality."""
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    sample_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    image_bytes = img_byte_arr.getvalue()
    
    # Test image processing pipeline
    result = await image_processor.process_image(image_bytes)
    
    assert result is not None
    assert hasattr(result, 'query_id')
    assert hasattr(result, 'results')
    assert hasattr(result, 'created_at')
    assert hasattr(result, 'processing_time')

@pytest.mark.asyncio
async def test_end_to_end(image_processor, sample_image):
    """Test the entire image processing pipeline."""
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    sample_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    image_bytes = img_byte_arr.getvalue()
    
    # Process image
    search_result = await image_processor.process_image(image_bytes)
    assert search_result is not None
    
    # Verify search result structure
    assert search_result.query_id is not None
    assert isinstance(search_result.results, list)
    assert search_result.processing_time > 0
    assert search_result.created_at is not None
    
    # If detections found, verify their structure
    if search_result.results:
        detection = search_result.results[0]
        assert hasattr(detection, 'bounding_box')
        assert hasattr(detection, 'confidence')
        if detection.product:
            assert hasattr(detection.product, 'id')
            assert hasattr(detection.product, 'name')
            assert hasattr(detection.product, 'image_url')

@pytest.mark.asyncio
async def test_api_endpoints():
    """Test the API endpoints."""
    # TODO: Implement API endpoint tests
    # This will require setting up a test FastAPI client
    pass

if __name__ == "__main__":
    # Create test data directory if it doesn't exist
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    
    # Run tests
    asyncio.run(pytest.main([__file__, "-v"])) 