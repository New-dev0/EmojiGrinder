import json
from typing import Optional, Any
import aioredis
import logging
from sources.emojis import GraphQLResponse
from config import settings

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        try:
            if settings.REDIS_ENABLED:
                self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
                self.available = True
            else:
                self.available = False
                logger.info("Redis cache is disabled via configuration")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching will be disabled.")
            self.available = False
        self.default_ttl = 3600  # Cache for 1 hour by default

    async def get(self, key: str) -> Optional[dict]:
        """Get value from cache"""
        if not self.available:
            return None
        
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.warning(f"Redis get operation failed: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value in cache"""
        if not self.available:
            return
        
        if ttl is None:
            ttl = self.default_ttl
        try:
            await self.redis.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.warning(f"Redis set operation failed: {e}")

    def get_search_key(self, query: str, first: int) -> str:
        """Generate cache key for search results"""
        return f"emoji:search:{query}:{first}"

    async def close(self):
        """Close Redis connection"""
        if not self.available:
            return
        
        try:
            await self.redis.close()
        except Exception as e:
            logger.warning(f"Redis close operation failed: {e}") 