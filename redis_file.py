from typing import Optional

from redis.asyncio import Redis

from configs.passwords import REDIS_DB, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT


class RedisStorage:
    def __init__(self, host: str = REDIS_HOST, port: int = REDIS_PORT, db: int = REDIS_DB,
                 password: Optional[str] = REDIS_PASSWORD, decode_responses: bool = True):
        self.redis = Redis(host=host, port=port, db=db, password=password, decode_responses=decode_responses)

    async def set(self, key: str, value: int = 0, expire: Optional[int] = None):
        await self.redis.set(name=key, value=value, ex=expire)

    async def get(self, key: str) -> Optional[int]:
        return await self.redis.get(name=key)

    # возвращает True или False
    async def exists(self, key: str) -> bool:
        return await self.redis.exists(key) > 0

    # возвращает 1 или 0
    async def delete(self, key: str) -> int:
        return await self.redis.delete(key)

    async def expire(self, key: str, seconds: int) -> bool:
        """Установить TTL (время жизни) ключа"""
        return await self.redis.expire(key, seconds)

    async def search_keys(self, pattern: str = "*") -> list[str]:
        return await self.redis.keys(pattern)

    async def ttl(self, key: str) -> int:
        """Получить оставшееся время жизни ключа (в секундах)"""
        return await self.redis.ttl(key)

    async def incr(self, key: str, amount: int = 1) -> int:
        """Увеличить значение по ключу (если оно число), возвращает новое значение"""
        return await self.redis.incr(key, amount)

    async def clear(self):
        await self.redis.flushdb()

    async def close(self):
        await self.redis.flushdb()
        await self.redis.close()


redis_storage = RedisStorage()


# print(asyncio.run(redis_storage.get('1234')))
