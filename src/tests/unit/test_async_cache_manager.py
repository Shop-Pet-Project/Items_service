import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from items_app.infrastructure.redis.cache.async_cache_manager import AsyncCacheManager


# --- Мок Redis ---
@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.scan_iter = MagicMock(return_value=async_iterator([]))
    return redis

# --- Мок сериализатора для Redis ---
@pytest.fixture
def mock_serializer():
    serializer = MagicMock()
    serializer.dumps.side_effect = lambda v: f"SER:{v}"
    serializer.loads.side_effect = lambda v: v.replace("SER:", "")
    return serializer


def async_iterator(items):
    async def _aiter():
        for item in items:
            yield item
    return _aiter()


# --- Фикстура инициализирующая AsyncCacheManager ---
@pytest.fixture
def cache(mock_redis, mock_serializer):
    return AsyncCacheManager(mock_redis, mock_serializer)


# --- Тесты ---
def test_generate_key(cache):
    assert cache.generate_key("a", 1, "b") == "a:1:b"

@pytest.mark.asyncio
async def test_set_calls_redis_with_serialized_value(cache, mock_redis, mock_serializer):
    await cache.set("key", "value", ex=42)
    mock_serializer.dumps.assert_called_once_with("value")
    mock_redis.set.assert_awaited_once_with("key", "SER:value", 42)

@pytest.mark.asyncio
async def test_get_returns_deserialized_value(cache, mock_redis, mock_serializer):
    mock_redis.get.return_value = "SER:value"
    result = await cache.get("key")
    mock_serializer.loads.assert_called_once_with("SER:value")
    assert result == "value"

@pytest.mark.asyncio
async def test_get_returns_none_if_not_found(cache, mock_redis):
    mock_redis.get.return_value = None
    assert await cache.get("missing") is None

@pytest.mark.asyncio
async def test_delete_calls_redis_delete(cache, mock_redis):
    mock_redis.delete.return_value = 2
    result = await cache.delete("k1", "k2")
    mock_redis.delete.assert_awaited_once_with("k1", "k2")
    assert result == 2

@pytest.mark.asyncio
async def test_delete_pattern_deletes_matching_keys(cache, mock_redis):
    mock_redis.scan_iter = MagicMock(return_value=async_iterator(["k1", "k2"]))
    mock_redis.delete.return_value = 2
    result = await cache.delete_pattern("prefix:*")
    mock_redis.delete.assert_awaited_once_with("k1", "k2")
    assert result == 2

@pytest.mark.asyncio
async def test_delete_pattern_returns_zero_if_no_keys(cache, mock_redis):
    mock_redis.scan_iter = MagicMock(return_value=async_iterator([]))
    result = await cache.delete_pattern("prefix:*")
    mock_redis.delete.assert_not_awaited()
    assert result == 0
