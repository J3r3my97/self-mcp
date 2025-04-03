# app/utils/cache.py
import asyncio
import hashlib
import json
import time
from typing import Any, Callable, Dict, Optional, Tuple

import structlog

logger = structlog.get_logger(__name__)


class LRUCache:
    """
    A simple LRU (Least Recently Used) cache implementation.
    """
    
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of items to store in the cache
            ttl: Time-to-live in seconds for cache entries
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.access_order: Dict[str, float] = {}
        self._lock = asyncio.Lock()
        
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        async with self._lock:
            if key not in self.cache:
                return None
            
            value, timestamp = self.cache[key]
            current_time = time.time()
            
            # Check if the entry has expired
            if current_time - timestamp > self.ttl:
                # Remove expired entry
                del self.cache[key]
                del self.access_order[key]
                return None
            
            # Update access time
            self.access_order[key] = current_time
            return value
    
    async def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        async with self._lock:
            current_time = time.time()
            
            # If cache is full, remove least recently used item
            if len(self.cache) >= self.max_size and key not in self.cache:
                # Find the least recently used key
                lru_key = min(self.access_order.items(), key=lambda x: x[1])[0]
                del self.cache[lru_key]
                del self.access_order[lru_key]
            
            # Add or update the cache entry
            self.cache[key] = (value, current_time)
            self.access_order[key] = current_time
    
    async def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if the key was deleted, False if it wasn't in the cache
        """
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                del self.access_order[key]
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all entries from the cache."""
        async with self._lock:
            self.cache.clear()
            self.access_order.clear()
    
    def __len__(self) -> int:
        """Get the number of items in the cache."""
        return len(self.cache)


# Global cache instance
_cache = LRUCache()


def generate_cache_key(obj: Any) -> str:
    """
    Generate a cache key from an object.
    
    Args:
        obj: Object to generate a key for
        
    Returns:
        String cache key
    """
    # Convert object to a stable string representation
    json_str = json.dumps(obj, sort_keys=True)
    # Generate hash
    return hashlib.md5(json_str.encode()).hexdigest()


async def cached(func: Callable, *args, **kwargs) -> Any:
    """
    Decorator to cache function calls.
    
    Args:
        func: Function to cache
        
    Returns:
        Cached result or new result
    """
    # Generate cache key from function name and arguments
    key_data = {
        "func": func.__name__,
        "args": args,
        "kwargs": kwargs
    }
    cache_key = generate_cache_key(key_data)
    
    # Try to get from cache
    cached_result = await _cache.get(cache_key)
    if cached_result is not None:
        logger.debug("Cache hit", func=func.__name__)
        return cached_result
    
    # Not in cache, call the function
    logger.debug("Cache miss", func=func.__name__)
    result = await func(*args, **kwargs)
    
    # Store in cache
    await _cache.set(cache_key, result)
    return result


# Get the global cache instance
def get_cache() -> LRUCache:
    """Get the global cache instance."""
    return _cache