# app/models/deepseek.py
import os
from typing import Any, Dict, List, Optional

import httpx

from .base import BaseModelProvider


class DeepSeekProvider(BaseModelProvider):
    """Implementation of BaseModelProvider for DeepSeek models."""
    
    # Available DeepSeek models
    AVAILABLE_MODELS = [
        "deepseek-chat",
        "deepseek-coder",
        "deepseek-llm-67b",
        # Add other models as they become available
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the DeepSeek provider.
        
        Args:
            api_key: DeepSeek API key, defaults to environment variable
        """
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key not provided and not found in environment")
        
        self.base_url = "https://api.deepseek.com/v1"
        self.default_model = "deepseek-chat"
    
    async def generate(self, 
                      prompt: str, 
                      max_tokens: int = 1000,
                      temperature: float = 0.7,
                      top_p: float = 1.0,
                      stop_sequences: Optional[List[str]] = None,
                      model: Optional[str] = None,
                      **kwargs) -> Dict[str, Any]:
        """Generate a completion for the prompt using DeepSeek's API."""
        # For DeepSeek, we convert this to a chat format for consistency
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
        """Generate a response for a chat conversation using DeepSeek's API."""
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
            payload["stop"] = stop_sequences
            
        # Add any additional parameters
        for key, value in kwargs.items():
            payload[key] = value
        
        # Make the API request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=120.0  # Longer timeout for model generation
            )
            
            if response.status_code != 200:
                error_msg = f"Error from DeepSeek API: {response.status_code} - {response.text}"
                raise Exception(error_msg)
                
            response_data = response.json()
            
            # Format the response
            result = {
                "provider": "deepseek",
                "model": model,
                "content": response_data["choices"][0]["message"]["content"],
                "raw_response": response_data
            }
            
            return result
    
    def get_available_models(self) -> List[str]:
        """Get the list of available DeepSeek models."""
        return self.AVAILABLE_MODELS