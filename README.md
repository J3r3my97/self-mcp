# Gate-Release.io

A fashion item detection and similarity search API built with FastAPI, PyTorch, and Firebase.

## Features

- Fashion item detection using Faster R-CNN
- Similarity search using Vision Transformer (ViT)
- Firebase integration for storage and database
- RESTful API endpoints
- Docker support for easy deployment

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Firebase project with Realtime Database and Storage
- Google Cloud service account credentials

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/gate-release.git
cd gate-release
```

### 2. Set up environment variables

Create a `.env` file in the root directory:

```bash
# API Settings
DEBUG=1
PORT=8000
CORS_ORIGINS=["*"]
ALLOWED_HOSTS=["*"]
MAX_REQUESTS_PER_MINUTE=60

# Firebase Settings
FIREBASE_DATABASE_URL=your_database_url
FIREBASE_STORAGE_BUCKET=your_storage_bucket

# Model Settings
MODEL_DEVICE=cpu
CONFIDENCE_THRESHOLD=0.5
```

### 3. Set up Firebase credentials

1. Create a `config` directory in the root
2. Place your Firebase service account JSON file as `config/service-account.json`

### 4. Run with Docker Compose

```bash
# Build and start the containers
docker-compose up --build

# To run in detached mode
docker-compose up -d
```

The API will be available at http://localhost:8000

### 5. Access the API documentation

Open your browser and navigate to:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

### 1. Production Environment Variables

Update the `.env` file with production settings:

```bash
# API Settings
DEBUG=0
PORT=8000
CORS_ORIGINS=["https://yourdomain.com"]
ALLOWED_HOSTS=["yourdomain.com"]
MAX_REQUESTS_PER_MINUTE=100

# Security Settings
ENABLE_HTTPS_REDIRECT=true

# Firebase Settings
FIREBASE_DATABASE_URL=your_production_database_url
FIREBASE_STORAGE_BUCKET=your_production_storage_bucket
```

### 2. Build and Deploy

```bash
# Build the Docker image
docker-compose build

# Deploy to your server
docker-compose up -d
```

### 3. Monitoring

Check the logs:
```bash
docker-compose logs -f
```

## API Endpoints

- `POST /api/v1/identify`: Upload an image for fashion item detection
- `GET /api/v1/search/{query_id}`: Retrieve search results
- `GET /api/v1/health`: Check API health status

## Testing

Run the test suite:
```bash
# Using Docker
docker-compose exec app pytest src/tests/

# Locally
cd src
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.