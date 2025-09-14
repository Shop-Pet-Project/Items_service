import pytest
from unittest.mock import AsyncMock, MagicMock


# --- Мок репозитория для работы с БД ---
@pytest.fixture
def mock_repo():
    return AsyncMock()


# --- Мок Redis для работы с кешем ---
@pytest.fixture
def mock_cache():
    cache = AsyncMock()
    cache.generate_key = MagicMock(side_effect=lambda *args: ":".join(args))
    return cache
