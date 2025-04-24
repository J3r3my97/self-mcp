import logging
import time
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ..database.repository import FirebaseRepository
from ..models.detector import FashionDetector
from ..models.similarity import SimilaritySearch
from ..services.image_processor import ImageProcessor
from ..utils.config import settings
from .schemas import DetectionResult, ErrorResponse, SearchResponse

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

router = APIRouter()
detector = FashionDetector()
similarity_search = SimilaritySearch()
repository = FirebaseRepository()
image_processor = ImageProcessor(repository)

@router.post(
    "/identify",
    response_model=SearchResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Identify fashion items in an image",
    description="Upload an image containing fashion items to identify and find similar products."
)
async def identify_fashion(
    file: UploadFile = File(..., description="Image file to process")
):
    try:
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
        result = await image_processor.process_image(content)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the image"
        )

@router.get(
    "/search/{query_id}",
    response_model=SearchResponse,
    responses={404: {"model": ErrorResponse}},
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
        logger.error(f"Error retrieving search results: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving search results"
        )

@router.get("/health")
async def health_check():
    return {"status": "healthy"} 