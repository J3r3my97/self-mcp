import os
from datetime import datetime
from typing import List

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi_mcp import add_mcp_server
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Pydantic models for structured response
class NewsletterResponse(BaseModel):
    title: str
    content: str
    summary: str
    sections: List[dict]
    sources: List[str]
    generated_at: datetime

app = FastAPI(
    title="Newsletter API",
    description="API for generating newsletters",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Initialize Anthropic client
client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

mcp_server = add_mcp_server(
    app,
    mount_path="/mcp",
    name="Newsletter Generation API",
    describe_all_responses=True,
    describe_full_response_schema=True
)

@mcp_server.tool()
async def generate_newsletter(topic: str) -> NewsletterResponse:
    """
    Generate a comprehensive newsletter about a specific topic using AI.
    
    Args:
        topic: The topic to generate a newsletter about. Can be any subject like 
              'artificial intelligence', 'climate change', 'space exploration', etc.
        
    Returns:
        A structured newsletter containing title, content, summary, sections, and sources
        
    Raises:
        HTTPException: If newsletter generation fails or topic is invalid
    """
    try:
        # Input validation
        if not topic or len(topic.strip()) < 2:
            raise HTTPException(status_code=400, detail="Topic must be at least 2 characters long")

        # Generate content using Claude
        message = await client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": f"""Generate a comprehensive newsletter about {topic}.
                Format the response as JSON with the following structure:
                {{
                    "title": "An engaging title",
                    "content": "Main article content",
                    "summary": "Brief executive summary",
                    "sections": [
                        {{"heading": "section heading", "content": "section content"}}
                    ],
                    "sources": ["list of credible sources"]
                }}
                
                Make it informative, engaging, and well-structured. Include recent developments
                and insights. Ensure all information is accurate and well-sourced."""
            }]
        )

        # Parse Claude's response
        # Note: You'll need to implement proper JSON parsing based on Claude's actual response format
        response_content = message.content[0].text
        # Add proper JSON parsing here

        # For now, using a simplified example
        newsletter = NewsletterResponse(
            title=f"The Latest Developments in {topic.title()}",
            content=response_content,  # This should be parsed from Claude's response
            summary=f"A comprehensive overview of recent developments in {topic}",
            sections=[
                {"heading": "Current Trends", "content": "..."},
                {"heading": "Future Outlook", "content": "..."},
                {"heading": "Expert Insights", "content": "..."}
            ],
            sources=[
                "Example Source 1",
                "Example Source 2"
            ],
            generated_at=datetime.utcnow()
        )

        return newsletter

    except anthropic.APIError as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Newsletter generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 