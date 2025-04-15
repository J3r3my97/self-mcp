# Weather MCP Server Technical Context

## Technology Stack
- Python 3.9
- FastAPI framework
- FastMCP for MCP implementation
- Google Cloud Run
- National Weather Service API

## Development Environment
- Docker for containerization
- GitHub for version control
- Cloud Build for CI/CD
- Cloud Run for deployment

## Key Dependencies
- fastapi-mcp>=0.1.8
- httpx for async HTTP calls
- pydantic for data validation
- uvicorn for ASGI server

## Technical Constraints
1. NWS API Rate Limits
   - Respect rate limiting
   - Implement caching where appropriate

2. Cloud Run Limitations
   - Stateless application design
   - Request timeout limits
   - Memory constraints

## Security Considerations
- No API keys required for NWS API
- HTTPS enforcement
- Input validation
- Rate limiting 