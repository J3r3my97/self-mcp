# Gate-Release.io Fashion Identification AI

A computer vision system that identifies fashion items from user-uploaded images, helping users discover and purchase fashion items they see in images.

## Features

- Process images containing fashion items
- Detect and isolate individual clothing items
- Classify items by category
- Extract attributes (color, pattern, material)
- Match against a database of known fashion products
- Return closest matches with purchase links

## Prerequisites

- Docker and Docker Compose
- Firebase service account key
- Python 3.12+ (for local development)

## Local Development

### Using Docker Compose

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gate-release.git
cd gate-release
```

2. Create a `.env` file in the root directory with the following variables:
```env
FIREBASE_DATABASE_URL=your_database_url
FIREBASE_STORAGE_BUCKET=your_storage_bucket
FIREBASE_SERVICE_ACCOUNT=base64:your_base64_encoded_service_account
```

3. Start the application:
```bash
docker-compose up --build
```

4. Access the API documentation at:
```
http://localhost:8000/docs
```

### Manual Setup (Optional)

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Place your Firebase service account key at `serviceAccountKey.json` in the root directory

4. Run the application:
```bash
cd src
uvicorn main:app --reload
```

## Deployment

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t gate-release:latest .
```

2. Run the container:
```bash
docker run -d \
  -p 8000:8000 \
  -e FIREBASE_DATABASE_URL=your_database_url \
  -e FIREBASE_STORAGE_BUCKET=your_storage_bucket \
  -e FIREBASE_SERVICE_ACCOUNT=base64:your_base64_encoded_service_account \
  gate-release:latest
```

### CI/CD Deployment

The project uses GitHub Actions for continuous deployment. To deploy:

1. Add the following secrets to your GitHub repository:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: Your Docker Hub access token
   - `FIREBASE_SERVICE_ACCOUNT`: Your base64-encoded Firebase service account

2. Push to the main branch to trigger deployment:
```bash
git push origin main
```

## API Documentation

The API documentation is available at `/docs` when running the application. Key endpoints include:

- `POST /identify`: Upload an image for fashion item identification
- `GET /search/{query_id}`: Retrieve search results
- `GET /health`: Check application health status

## Security Considerations

- The Firebase service account key is handled securely through environment variables
- Rate limiting is implemented to prevent abuse
- CORS is configured to restrict access to specified origins
- HTTPS is enforced in production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.