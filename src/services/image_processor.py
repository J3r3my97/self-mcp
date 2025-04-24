import io
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List

import numpy as np
from PIL import Image

from api.schemas import DetectionResponse, ProductResponse, SearchResponse
from database.models import Category, Product
from database.repository import FirebaseRepository
from models.fashion_detector import FashionDetector
from models.similarity_search import SimilaritySearch

# Configure logging
logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self, fashion_detector: FashionDetector, similarity_search: SimilaritySearch, repository: FirebaseRepository):
        self.fashion_detector = fashion_detector
        self.similarity_search = similarity_search
        self.repository = repository
        
    async def process_image(self, image_data: bytes) -> SearchResponse:
        """
        Process an image to detect fashion items and find similar products.
        
        Args:
            image_data: bytes of the image file
            
        Returns:
            SearchResponse: Object containing detection results and similar products
        """
        try:
            start_time = datetime.now()
            
            # Get detections from fashion detector
            detections = self.fashion_detector.forward(image_data)
            
            # Get embeddings for the whole image
            embeddings = self.fashion_detector.get_embeddings(image_data)
            
            # Search for similar products
            similar_products = await self.similarity_search.search(embeddings)
            
            # Create detection results
            detection_results = []
            for detection in detections:
                box = detection['box']
                confidence = detection['confidence']
                
                # Get the most similar product for this detection
                product = similar_products[0] if similar_products else None
                similarity_score = product.get('similarity_score', 0.0) if product else 0.0
                
                # Convert product dict to ProductResponse if exists
                product_response = None
                if product:
                    product_response = ProductResponse(
                        id=product.get('id', ''),
                        brand=product.get('brand', ''),
                        name=product.get('name', ''),
                        price=product.get('price', 0.0),
                        currency=product.get('currency', 'USD'),
                        source_url=product.get('source_url', ''),
                        image_url=product.get('image_url', '')
                    )
                
                detection_results.append(
                    DetectionResponse(
                        product=product_response,
                        similarity_score=similarity_score,
                        bounding_box={
                            'x1': box[0],
                            'y1': box[1],
                            'x2': box[2],
                            'y2': box[3]
                        },
                        confidence=confidence
                    )
                )
            
            # Create search result
            search_result = SearchResponse(
                query_id=str(uuid.uuid4()),
                results=detection_results,
                processing_time=(datetime.now() - start_time).total_seconds(),
                created_at=datetime.now()
            )
            
            # Save search result
            await self.repository.save_search_result(search_result)
            
            return search_result
                
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise 