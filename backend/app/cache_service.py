"""
Cache Service using Redis
Implements multi-level caching based on Gemini recommendations
"""
import redis.asyncio as redis
import json
import hashlib
from typing import Optional, Any, Dict
from datetime import timedelta
from loguru import logger

class CacheService:
    """
    Redis-based cache service for improving performance
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_ttl = timedelta(minutes=5)
        
    def _generate_key(self, operation: str, user_id: str, params: Dict = None) -> str:
        """Generate a unique cache key"""
        key_parts = [operation, user_id]
        if params:
            # Sort params to ensure consistent keys
            sorted_params = json.dumps(params, sort_keys=True)
            key_parts.append(hashlib.md5(sorted_params.encode()).hexdigest())
        return ":".join(key_parts)
    
    async def get(self, operation: str, user_id: str, params: Dict = None) -> Optional[Any]:
        """Get cached value"""
        key = self._generate_key(operation, user_id, params)        try:
            cached = await self.redis.get(key)
            if cached:
                logger.debug(f"Cache HIT for key: {key}")
                return json.loads(cached)
            logger.debug(f"Cache MISS for key: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache GET error: {e}")
            return None
    
    async def set(self, operation: str, user_id: str, value: Any, 
                  params: Dict = None, ttl: timedelta = None) -> bool:
        """Set cached value with TTL"""
        key = self._generate_key(operation, user_id, params)
        ttl = ttl or self.default_ttl
        
        try:
            await self.redis.setex(
                key,
                int(ttl.total_seconds()),
                json.dumps(value)
            )
            logger.debug(f"Cache SET for key: {key}, TTL: {ttl}")
            return True
        except Exception as e:
            logger.error(f"Cache SET error: {e}")
            return False
    
    async def invalidate_user_cache(self, user_id: str) -> int:
        """Invalidate all cache for a specific user"""
        pattern = f"*:{user_id}:*"        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self.redis.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries for user {user_id}")
                return len(keys)
            return 0
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = await self.redis.info()
            return {
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "connected_clients": info.get("connected_clients", 0)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}