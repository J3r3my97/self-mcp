# Gate-Release.io

A FastAPI-based application for detecting fashion items in images and finding similar products.

## Features

- Image-based fashion item detection
- Similar product search
- User authentication and authorization
- Rate limiting
- Health monitoring
- Admin dashboard

## Tech Stack

- **Backend**: FastAPI
- **Database**: Firebase Realtime Database
- **Storage**: Firebase Storage
- **Authentication**: JWT with OAuth2
- **ML Models**: 
  - Object Detection: Faster R-CNN
  - Feature Extraction: ViT (Vision Transformer)
- **Cloud**: Google Cloud Platform
  - Secret Manager for secure key storage
  - Cloud Storage for model files

## Project Structure

```
src/
├── api/
│   ├── auth.py           # Authentication endpoints
│   ├── endpoints.py      # Main API endpoints
│   └── schemas.py        # Pydantic models
├── database/
│   ├── models.py         # Database models
│   └── repository.py     # Firebase operations
├── models/
│   ├── fashion_detector.py  # ML model for detection
│   └── similarity_search.py # Similarity search logic
├── services/
│   ├── auth_service.py   # Authentication logic
│   └── image_processor.py # Image processing service
└── utils/
    ├── config.py         # Application configuration
    └── firebase_config.py # Firebase setup
```

## Setup

1. **Environment Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Firebase Configuration**
- Create a Firebase project
- Download service account key
- Set environment variables:
```bash
export FIREBASE_DATABASE_URL="your-database-url"
export FIREBASE_STORAGE_BUCKET="your-storage-bucket"
export FIREBASE_SERVICE_ACCOUNT="base64-encoded-service-account"
```

3. **Google Cloud Setup**
- Create a GCP project
- Enable Secret Manager API
- Create secrets:
```bash
gcloud secrets create SECRET_KEY --project=your-project-id
gcloud secrets versions add SECRET_KEY --data-file=- <<< "your-secret-key"
```

4. **Model Setup**
- Models are automatically downloaded to `src/models/huggingface_models/`
- First run might take time to download models

## Running the Application

```bash
# Start the server
uvicorn src.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- OpenAPI Schema: http://localhost:8000/openapi.json

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user info

### Main Features
- `POST /api/v1/identify` - Upload image for fashion detection
- `GET /api/v1/search/{query_id}` - Get search results
- `GET /api/v1/health` - Check system health

### Admin
- `GET /api/v1/admin/stats` - Get system statistics (admin only)

## Authentication

The API uses JWT tokens for authentication:
1. Register a user
2. Login to get a token
3. Use the token in the Authorization header:
```
Authorization: Bearer <your-token>
```

## Importing to Postman

1. Get the OpenAPI schema:
```bash
curl http://localhost:8000/openapi.json > openapi.json
```

2. Import into Postman:
- Open Postman
- Click "Import"
- Upload the `openapi.json` file
- Set up OAuth2 authentication:
  - Token URL: http://localhost:8000/api/v1/auth/login
  - Grant Type: Password Credentials
  - Username: your-email
  - Password: your-password

## Security Notes

- All secrets are stored in Google Cloud Secret Manager
- JWT tokens expire after 30 minutes
- Rate limiting is enabled (60 requests per minute)
- HTTPS redirection can be enabled in production

## Development

- Use `black` for code formatting
- Run tests with `pytest`
- Enable debug mode for detailed logs
- Use the `/health` endpoint to monitor system status

## Production Deployment

1. Set up environment variables:
```bash
export DEBUG=false
export ENABLE_HTTPS_REDIRECT=true
export SECRET_KEY=$(gcloud secrets versions access latest --secret=SECRET_KEY)
```

2. Use a production-grade server:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

3. Set up a reverse proxy (nginx) for HTTPS
4. Configure CORS for your domain
5. Set up monitoring and logging