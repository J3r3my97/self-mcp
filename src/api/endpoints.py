import logging
import time
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from api.schemas import DetectionResult, ErrorResponse, HealthResponse, SearchResponse
from database.repository import FirebaseRepository
from models.fashion_detector import FashionDetector
from models.similarity_search import SimilaritySearch
from services.image_processor import ImageProcessor
from utils.config import settings
from utils.firebase_config import initialize_firebase

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize Firebase
if not initialize_firebase():
    raise RuntimeError("Failed to initialize Firebase")

router = APIRouter()

# Initialize components
detector = FashionDetector()
repository = FirebaseRepository()
similarity_search = SimilaritySearch(repository)
image_processor = ImageProcessor(detector, similarity_search, repository)

# Rate limiting dictionary
request_counts: Dict[str, Dict[str, Any]] = {}

@router.post(
    "/identify",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Identify fashion items in an image",
    description="Upload an image containing fashion items to identify and find similar products."
)
async def identify_fashion(
    request: Request,
    file: UploadFile = File(..., description="Image file to process")
):
    try:
        # Rate limiting
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean up old entries (older than 1 minute)
        global request_counts
        request_counts = {
            ip: data for ip, data in request_counts.items()
            if current_time - data['timestamp'] < 60
        }
        
        # Check rate limit
        if client_ip in request_counts:
            if request_counts[client_ip]['count'] >= settings.MAX_REQUESTS_PER_MINUTE:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later."
                )
            request_counts[client_ip]['count'] += 1
        else:
            request_counts[client_ip] = {'count': 1, 'timestamp': current_time}
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE} bytes"
            )
        
        # Process image
        logger.info(f"Processing image: {file.filename}")
        start_time = time.time()
        result = await image_processor.process_image(content)
        processing_time = time.time() - start_time
        
        # Log request details
        logger.info(f"Request completed - IP: {client_ip}, Time: {processing_time:.2f}s")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the image"
        )

@router.get(
    "/search/{query_id}",
    response_model=SearchResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Get search results by query ID",
    description="Retrieve the results of a previous image search by its query ID."
)
async def get_search_results(query_id: str):
    try:
        # Get search results from repository
        result = await repository.get_search_result(query_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Search results not found for query ID: {query_id}"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving search results: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving search results"
        )

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check system health",
    description="Returns the current health status of the system and its components."
)
async def health_check() -> Dict[str, Any]:
    try:
        # Check Firebase connection
        firebase_status = await repository.check_connection()
        
        # Check model status
        model_status = detector.check_status()
        
        # Check storage status
        storage_status = await repository.check_storage()
        
        return {
            "status": "healthy",
            "components": {
                "firebase": firebase_status,
                "model": model_status,
                "storage": storage_status
            },
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        } 