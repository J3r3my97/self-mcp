# Weather MCP Server

A Model Context Protocol (MCP) server that provides weather information tools to AI agents. The server exposes weather-related functionality through a standardized MCP interface, making it easy for AI agents to access and understand weather data.

## Features

- Weather forecast retrieval
- Weather alerts system
- Current conditions reporting
- US-based weather data
- Cloud Run deployment
- MCP-compliant API endpoints

## Prerequisites

- Python 3.9+
- Docker (for local development and deployment)
- Google Cloud SDK (for deployment)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd weather-mcp-server
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Local Development

1. Start the server:
```bash
uvicorn app.main:app --reload --port 8080
```

2. Access the API documentation:
- OpenAPI UI: http://localhost:8080/docs
- MCP endpoint: http://localhost:8080/mcp

## Testing

Run the test suite:
```bash
pytest tests/
```

For coverage report:
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

## Deployment

The server is configured to deploy to Google Cloud Run using Cloud Build:

1. Set up Google Cloud project:
```bash
gcloud config set project YOUR_PROJECT_ID
```

2. Enable required APIs:
```bash
gcloud services enable cloudbuild.googleapis.com run.googleapis.com
```

3. Deploy using Cloud Build:
```bash
gcloud builds submit
```

## API Endpoints

### MCP Tools

1. `get_weather_forecast`
   - Input: latitude (float), longitude (float)
   - Returns: Detailed weather forecast

2. `get_weather_alerts`
   - Input: state (str, two-letter US state code)
   - Returns: Active weather alerts for the state

3. `get_current_conditions`
   - Input: latitude (float), longitude (float)
   - Returns: Current weather conditions

### Health Check

- `GET /health`: Server health status

## Data Source

This service uses the National Weather Service (NWS) API for weather data. No API key is required, but please follow their [usage guidelines](https://www.weather.gov/documentation/services-web-api).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.