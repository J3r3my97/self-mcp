# app/models/factory.py
from typing import Dict, Optional, Type

from .base import BaseModelProvider
from .claude import ClaudeProvider
from .deepseek import DeepSeekProvider


class ModelFactory:
    """Factory class for creating model providers."""
    
    # Registry of available providers
    PROVIDERS = {
        "claude": ClaudeProvider,
        "deepseek": DeepSeekProvider,
        # Add more providers as they are implemented
    }
    
    @classmethod
    def create_provider(cls, provider_name: str, api_key: Optional[str] = None) -> BaseModelProvider:
        """
        Create a model provider instance based on provider name.
        
        Args:
            provider_name: Name of the model provider
            api_key: API key for the provider (optional)
            
        Returns:
            An instance of the requested model provider
        
        Raises:
            ValueError: If the requested provider is not available
        """
        if provider_name not in cls.PROVIDERS:
            available_providers = ", ".join(cls.PROVIDERS.keys())
            raise ValueError(f"Provider '{provider_name}' not available. Choose from: {available_providers}")
        
        provider_class = cls.PROVIDERS[provider_name]
        return provider_class(api_key=api_key)
    
    @classmethod
    def list_providers(cls) -> Dict[str, Type[BaseModelProvider]]:
        """
        Get a dictionary of all available providers.
        
        Returns:
            Dictionary mapping provider names to provider classes
        """
        return cls.PROVIDERS.copy()
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseModelProvider]) -> None:
        """
        Register a new provider.
        
        Args:
            name: Name for the provider
            provider_class: Class implementing BaseModelProvider
        """
        cls.PROVIDERS[name] = provider_class