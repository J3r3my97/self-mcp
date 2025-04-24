import time
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ..models.detector import FashionDetector
from ..models.similarity import SimilaritySearch
from ..utils.config import settings
from .schemas import DetectionResult, ErrorResponse

router = APIRouter()
detector = FashionDetector()
similarity_search = SimilaritySearch()

@router.post("/identify", response_model=DetectionResult)
async def identify_fashion(file: UploadFile = File(...)):
    try:
        start_time = time.time()
        
        # Validate file
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Process image
        detections = await detector.process_image(file)
        
        # Find similar products
        results = []
        for detection in detections:
            similar_products = similarity_search.search(detection['embedding'])
            results.extend(similar_products)
        
        processing_time = time.time() - start_time
        
        return DetectionResult(
            items=results,
            processing_time=processing_time
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                detail=str(e),
                code="INTERNAL_SERVER_ERROR"
            ).dict()
        )

@router.get("/health")
async def health_check():
    return {"status": "healthy"} 