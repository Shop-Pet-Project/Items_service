from typing import Optional, AsyncIterator
from redis.asyncio import Redis as AsyncRedis
from items_app.infrastructure.config import config


class AsyncRedisClient(AsyncRedis):
    def __init__(self):
        super().__init__(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True,
        )
