# app/api/routes.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas import (
    ChatRequest,
    ErrorResponse,
    GenerateRequest,
    ModelResponse,
    ProviderInfo,
    ProvidersResponse,
)
from app.models.factory import ModelFactory
from app.utils.settings import get_settings

router = APIRouter()


@router.post("/generate", response_model=ModelResponse)
async def generate(request: GenerateRequest, settings=Depends(get_settings)):
    """
    Generate text using a specified model provider.
    """
    try:
        # Get the API key - use request override if provided, else use from settings
        api_key = request.api_key or getattr(settings, f"{request.provider.upper()}_API_KEY", None)
        
        # Create the provider
        provider = ModelFactory.create_provider(request.provider, api_key)
        
        # Extract additional parameters
        additional_params = request.additional_params or {}
        
        # Generate the response
        response = await provider.generate(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stop_sequences=request.stop_sequences,
            model=request.model,
            **additional_params
        )
        
        return response
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/chat", response_model=ModelResponse)
async def chat(request: ChatRequest, settings=Depends(get_settings)):
    """
    Generate a chat completion using a specified model provider.
    """
    try:
        # Get the API key - use request override if provided, else use from settings
        api_key = request.api_key or getattr(settings, f"{request.provider.upper()}_API_KEY", None)
        
        # Create the provider
        provider = ModelFactory.create_provider(request.provider, api_key)
        
        # Extract additional parameters
        additional_params = request.additional_params or {}
        
        # Format messages
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Generate the response
        response = await provider.chat(
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stop_sequences=request.stop_sequences,
            model=request.model,
            **additional_params
        )
        
        return response
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")


@router.get("/providers", response_model=ProvidersResponse)
async def list_providers(settings=Depends(get_settings)):
    """
    List all available model providers and their models.
    """
    try:
        providers_info = []
        
        for provider_name, provider_class in ModelFactory.list_providers().items():
            # Try to create the provider with the API key from settings
            api_key = getattr(settings, f"{provider_name.upper()}_API_KEY", None)
            
            try:
                provider = provider_class(api_key)
                models = provider.get_available_models()
            except (ValueError, Exception):
                # If API key is missing or invalid, just list the provider without models
                models = ["API key required to list models"]
            
            providers_info.append(
                ProviderInfo(
                    name=provider_name,
                    models=models
                )
            )
        
        return ProvidersResponse(providers=providers_info)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list providers: {str(e)}")
    

