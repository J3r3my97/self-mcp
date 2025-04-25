from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.api.endpoints import router as api_router
from src.utils.config import settings
from src.utils.firebase_config import initialize_firebase

# Initialize Firebase
if not initialize_firebase():
    raise RuntimeError("Failed to initialize Firebase")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for fashion item detection and similarity search",
    version="1.0.0",
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=settings.GZIP_MIN_SIZE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

if settings.ENABLE_HTTPS_REDIRECT:
    app.add_middleware(HTTPSRedirectMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


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

    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
