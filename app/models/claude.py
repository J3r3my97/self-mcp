# app/models/claude.py
import os
from typing import Any, Dict, List, Optional

import anthropic
import httpx

from app.api.schemas import Message, ModelResponse
from app.utils.settings import get_settings

from .base import BaseModelProvider


class ClaudeProvider(BaseModelProvider):
    """Implementation of the BaseModelProvider for Anthropic's Claude."""
    
    # Model IDs for Claude
    AVAILABLE_MODELS = [
        "claude-3-5-sonnet-20240620",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        # Add other models as they become available
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Claude provider.
        
        Args:
            api_key: Anthropic API key, defaults to environment variable
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided and not found in environment")
        
        self.base_url = "https://api.anthropic.com/v1"
        self.default_model = "claude-3-sonnet-20240229"
    
    async def generate(self, 
                      prompt: str, 
                      max_tokens: int = 1000,
                      temperature: float = 0.7,
                      top_p: float = 1.0,
                      stop_sequences: Optional[List[str]] = None,
                      model: Optional[str] = None,
                      **kwargs) -> Dict[str, Any]:
        """Generate a completion for the prompt using Claude's API."""
        # Convert to chat format for Claude API
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, max_tokens, temperature, top_p, stop_sequences, model, **kwargs)
    
    async def chat(self,
                  messages: List[Dict[str, str]],
                  max_tokens: int = 1000,
                  temperature: float = 0.7,
                  top_p: float = 1.0,
                  stop_sequences: Optional[List[str]] = None,
                  model: Optional[str] = None,
                  **kwargs) -> Dict[str, Any]:
        """Generate a response for a chat conversation using Claude's API."""
        model = model or self.default_model
        
        # Validate the model
        if model not in self.AVAILABLE_MODELS:
            raise ValueError(f"Model {model} not available. Choose from {self.AVAILABLE_MODELS}")
        
        # Prepare the request payload
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }
        
        if stop_sequences:
            payload["stop_sequences"] = stop_sequences
            
        # Add any additional parameters
        for key, value in kwargs.items():
            payload[key] = value
        
        # Make the API request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                json=payload,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                timeout=120.0  # Longer timeout for model generation
            )
            
            if response.status_code != 200:
                error_msg = f"Error from Claude API: {response.status_code} - {response.text}"
                raise Exception(error_msg)
                
            response_data = response.json()
            
            # Format the response
            result = {
                "provider": "claude",
                "model": model,
                "content": response_data["content"][0]["text"],
                "raw_response": response_data
            }
            
            return result
    
    def get_available_models(self) -> List[str]:
        """Get the list of available Claude models."""
        return self.AVAILABLE_MODELS


class ClaudeModel:
    def __init__(self):
        settings = get_settings()
        self.client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)
        self.default_model = "claude-3-sonnet-20240229"
    
    async def generate(self, messages: List[Message], max_tokens: int = 1000, 
                      temperature: float = 0.7, model: str = None) -> ModelResponse:
        """Generate a response using Claude API."""
        model_name = model or self.default_model
        
        # Convert messages to Anthropic format
        anthropic_messages = [
            {"role": msg.role, "content": msg.content} 
            for msg in messages
        ]
        
        # Call Claude API
        response = await self.client.messages.create(
            model=model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=anthropic_messages
        )
        
        # Extract usage information
        usage = {
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens
        }
        
        # Create and return response
        return ModelResponse(
            content=response.content[0].text,
            model=model_name,
            usage=usage
        )