import io

import numpy as np
import pytest
from PIL import Image, ImageDraw

from src.database.repository import FirebaseRepository
from src.models.fashion_detector import FashionDetector
from src.models.similarity_search import SimilaritySearch
from src.services.image_processor import ImageProcessor


@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    # Create a 224x224 RGB image with a black background
    img = Image.new("RGB", (224, 224), color="black")

    # Draw a white square in the middle
    draw = ImageDraw.Draw(img)
    square_size = 100
    x1 = (224 - square_size) // 2
    y1 = (224 - square_size) // 2
    x2 = x1 + square_size
    y2 = y1 + square_size
    draw.rectangle([x1, y1, x2, y2], fill="white")

    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()


@pytest.fixture
def fashion_detector():
    """Initialize FashionDetector with CPU device."""
    return FashionDetector(device="cpu")


@pytest.fixture
def repository():
    """Initialize FirebaseRepository."""
    return FirebaseRepository()


@pytest.fixture
def similarity_search(repository):
    """Initialize SimilaritySearch."""
    return SimilaritySearch(repository=repository)


@pytest.fixture
def image_processor(fashion_detector, similarity_search, repository):
    """Initialize ImageProcessor."""
    return ImageProcessor(
        detector=fashion_detector,
        similarity_search=similarity_search,
        repository=repository,
    )
