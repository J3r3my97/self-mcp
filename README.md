# Model Context Protocol (MCP) App

A lightweight, Docker-based application that provides a unified API for interacting with various Large Language Models (LLMs) like Claude, DeepSeek, and more.

## Features

- 🚀 **Fast API**: Built with FastAPI for high performance and asyncio support
- 🔄 **Model Switching**: Easily switch between different LLM providers
- 🐳 **Containerized**: Ready to deploy with Docker
- 🔌 **Extensible**: Add new model providers with minimal code
- 🧠 **Context Protocol**: Support for maintaining conversation context
- 💾 **Caching**: Simple response caching for improved performance
- 📊 **Logging**: Structured logging for better observability

## Quick Start

### Prerequisites

- Docker and Docker Compose
- API keys for the LLM providers you want to use

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mcp-app.git
   cd mcp-app
   ```

2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

3. Add your API keys to the `.env` file:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   ```

4. Build and start the Docker container:
   ```bash
   docker-compose up -d
   ```

5. The API will be available at `http://localhost:8000`

## API Endpoints

### List Available Providers

```
GET /api/providers
```

Returns a list of available model providers and their models.

### Generate Text

```
POST /api/generate
```

Request body:
```json
{
  "provider": "claude",
  "model": "claude-3-sonnet-20240229",
  "prompt": "Write a short story about a robot learning to paint.",
  "max_tokens": 1000,
  "temperature": 0.7
}
```

### Chat Completion

```
POST /api/chat
```

Request body:
```json
{
  "provider": "deepseek",
  "messages": [
    {"role": "user", "content": "Hello, how are you?"}
  ],
  "max_tokens": 500,
  "temperature": 0.8
}
```

## Cloud Deployment Options

### AWS Elastic Container Service (ECS)

1. Create an ECR repository
   ```bash
   aws ecr create-repository --repository-name mcp-app
   ```

2. Build and push the Docker image
   ```bash
   $(aws ecr get-login --no-include-email)
   docker build -t your-aws-account-id.dkr.ecr.region.amazonaws.com/mcp-app:latest .
   docker push your-aws-account-id.dkr.ecr.region.amazonaws.com/mcp-app:latest
   ```

3. Create an ECS cluster using AWS Fargate
   - Use the AWS Console or CLI to create the cluster
   - Create a task definition using the ECR image
   - Deploy the task as a service

### Google Cloud Run

1. Build and push to Google Container Registry
   ```bash
   gcloud builds submit --tag gcr.io/your-project-id/mcp-app
   ```

2. Deploy to Cloud Run
   ```bash
   gcloud run deploy mcp-app --image gcr.io/your-project-id/mcp-app --platform managed
   ```

3. Configure environment variables in the Cloud Run console

### Digital Ocean App Platform

1. Create a new app in the Digital Ocean dashboard
2. Connect your GitHub repository
3. Configure the app to use the Dockerfile for deployment
4. Add environment variables for your API keys
5. Deploy the app

## Adding a New Model Provider

1. Create a new provider class in `app/models/` that extends `BaseModelProvider`
2. Implement the required methods: `generate`, `chat`, and `get_available_models`
3. Register the provider in `app/models/factory.py`

Example:
```python
from .base import BaseModelProvider
from .new_provider import NewProvider

class ModelFactory:
    PROVIDERS = {
        "claude": ClaudeProvider,
        "deepseek": DeepSeekProvider,
        "new_provider": NewProvider,
    }
    # ...
```

## Development

### Local Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys

4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

### Running Tests

```bash
pytest
```

## License

MIT License
