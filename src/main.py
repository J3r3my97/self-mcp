from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.endpoints import router as api_router
from .utils.config import settings
from .utils.firebase_config import initialize_firebase

app = FastAPI(
    title="Gate-Release.io API",
    description="Fashion item identification and search API",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase
@app.on_event("startup")
async def startup_event():
    if not initialize_firebase():
        raise Exception("Failed to initialize Firebase")

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Gate-Release.io API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/live_demo")
async def live_demo():
    return {"status": "live_demo"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
