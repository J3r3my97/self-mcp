# app/api/schemas.py
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Message in a conversation."""
    role: str = Field(..., description="The role of the message sender (system, user, or assistant)")
    content: str = Field(..., description="The content of the message")


class GenerateRequest(BaseModel):
    """Request schema for text generation."""
    provider: str = Field(..., description="LLM provider (e.g., claude, deepseek)")
    model: Optional[str] = Field(None, description="Specific model to use (provider-dependent)")
    prompt: str = Field(..., description="Text prompt for generation")
    max_tokens: int = Field(1000, description="Maximum tokens to generate")
    temperature: float = Field(0.7, description="Sampling temperature (0-1)")
    top_p: float = Field(1.0, description="Nucleus sampling parameter (0-1)")
    stop_sequences: Optional[List[str]] = Field(None, description="Sequences that stop generation")
    api_key: Optional[str] = Field(None, description="Optional API key override")
    additional_params: Optional[Dict[str, Any]] = Field(None, description="Additional model-specific parameters")


class ChatRequest(BaseModel):
    """Request schema for chat completion."""
    provider: str = Field(..., description="LLM provider (e.g., claude, deepseek)")
    model: Optional[str] = Field(None, description="Specific model to use (provider-dependent)")
    messages: List[Message] = Field(..., description="List of conversation messages")
    max_tokens: int = Field(1000, description="Maximum tokens to generate")
    temperature: float = Field(0.7, description="Sampling temperature (0-1)")
    top_p: float = Field(1.0, description="Nucleus sampling parameter (0-1)")
    stop_sequences: Optional[List[str]] = Field(None, description="Sequences that stop generation")
    api_key: Optional[str] = Field(None, description="Optional API key override")
    additional_params: Optional[Dict[str, Any]] = Field(None, description="Additional model-specific parameters")


class ModelRequest(BaseModel):
    messages: List[Message] = Field(..., description="The conversation messages")
    max_tokens: Optional[int] = Field(1000, description="Maximum number of tokens to generate")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature")
    model: Optional[str] = Field(None, description="Model to use for completion")


class ModelResponse(BaseModel):
    """Response schema for model completions."""
    provider: str = Field(..., description="Provider that generated the response")
    model: str = Field(..., description="Model that generated the response")
    content: str = Field(..., description="Generated content")
    raw_response: Optional[Dict[str, Any]] = Field(None, description="Raw response from the model provider")
    usage: Dict[str, int] = Field(..., description="Token usage information")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ProviderInfo(BaseModel):
    """Information about a model provider."""
    name: str = Field(..., description="Provider name")
    models: List[str] = Field(..., description="Available models")


class ProvidersResponse(BaseModel):
    """Response schema for listing providers."""
    providers: List[ProviderInfo] = Field(..., description="List of available providers and their models")