"""
Redis 工具模块
"""
import redis.asyncio as redis
from config import settings

# Redis 客户端单例
_redis_client = None


async def get_redis_client() -> redis.Redis:
    """获取 Redis 客户端实例"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return _redis_client


async def close_redis_client():
    """关闭 Redis 客户端连接"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def check_ip_rate_limit(
    ip_address: str,
    limit: int = 15,
    ttl_seconds: int = 86400  # 24 小时
) -> tuple[bool, int]:
    """
    检查 IP 是否超过频率限制
    
    Args:
        ip_address: IP 地址
        limit: 允许的请求次数
        ttl_seconds: 过期时间（秒），默认 24 小时
        
    Returns:
        (是否允许, 当前次数)
    """
    redis_client = await get_redis_client()
    key = f"rate_limit:guestbook:{ip_address}"
    
    # 原子操作：INCR + EXPIRE
    current_count = await redis_client.incr(key)
    
    # 如果是第一次访问，设置过期时间
    if current_count == 1:
        await redis_client.expire(key, ttl_seconds)
    
    # 检查是否超过限制
    is_allowed = current_count <= limit
    
    return is_allowed, current_count


async def get_ip_usage(ip_address: str) -> int:
    """
    获取 IP 当前的使用次数
    
    Args:
        ip_address: IP 地址
        
    Returns:
        当前使用次数
    """
    redis_client = await get_redis_client()
    key = f"rate_limit:guestbook:{ip_address}"
    count = await redis_client.get(key)
    return int(count) if count else 0
