# app/models/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class BaseModelProvider(ABC):
    """Base class for all LLM model providers."""
    
    @abstractmethod
    async def generate(self, 
                      prompt: str, 
                      max_tokens: int = 1000,
                      temperature: float = 0.7,
                      top_p: float = 1.0,
                      stop_sequences: Optional[List[str]] = None,
                      **kwargs) -> Dict[str, Any]:
        """
        Generate a completion for the given prompt.
        
        Args:
            prompt: The input text prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0-1)
            top_p: Controls diversity via nucleus sampling
            stop_sequences: List of sequences that cause generation to stop
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dictionary containing the generated response and metadata
        """
        pass
    
    @abstractmethod
    async def chat(self,
                  messages: List[Dict[str, str]],
                  max_tokens: int = 1000,
                  temperature: float = 0.7,
                  top_p: float = 1.0,
                  stop_sequences: Optional[List[str]] = None,
                  **kwargs) -> Dict[str, Any]:
        """
        Generate a response for a chat conversation.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0-1)
            top_p: Controls diversity via nucleus sampling
            stop_sequences: List of sequences that cause generation to stop
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dictionary containing the generated response and metadata
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get the list of available models from this provider.
        
        Returns:
            List of model identifiers
        """
        pass