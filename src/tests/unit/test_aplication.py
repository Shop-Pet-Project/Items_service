import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from items_app.application.application import ItemApplications
from items_app.application.application_exceptions import ItemNotFound

@pytest.mark.asyncio
async def test_create_item_success():
    repo = AsyncMock()
    item = MagicMock()
    repo.add_item.return_value = item

    result = await ItemApplications.create_item(item, repo)

    repo.add_item.assert_awaited_once_with(item_data=item)
    repo.commit.assert_awaited_once()
    assert result is item

@pytest.mark.asyncio
async def test_create_item_failure_rolls_back():
    repo = AsyncMock()
    item = MagicMock()
    repo.add_item.side_effect = Exception("DB error")

    with pytest.raises(Exception):
        await ItemApplications.create_item(item, repo)

    repo.rollback.assert_awaited_once()
    repo.commit.assert_not_called()

@pytest.mark.asyncio
async def test_fetch_item_by_id_found():
    repo = AsyncMock()
    item_id = uuid4()
    fake_item = MagicMock()
    repo.get_item_by_id.return_value = fake_item

    result = await ItemApplications.fetch_item_by_id(item_id, repo)

    repo.get_item_by_id.assert_awaited_once_with(item_id=item_id)
    assert result is fake_item

@pytest.mark.asyncio
async def test_fetch_item_by_id_not_found():
    repo = AsyncMock()
    item_id = uuid4()
    repo.get_item_by_id.return_value = None

    with pytest.raises(ItemNotFound):
        await ItemApplications.fetch_item_by_id(item_id, repo)

@pytest.mark.asyncio
async def test_fetch_all_items_success():
    repo = AsyncMock()
    items = [MagicMock(), MagicMock()]
    repo.get_items.return_value = items

    result = await ItemApplications.fetch_all_items(0, 10, repo)

    repo.get_items.assert_awaited_once_with(0, 10)
    assert result == items

@pytest.mark.asyncio
async def test_update_item_data_success():
    repo = AsyncMock()
    item = MagicMock()
    repo.update_item.return_value = item

    result = await ItemApplications.update_item_data(item, repo)

    repo.update_item.assert_awaited_once_with(updated_item_data=item)
    repo.commit.assert_awaited_once()
    assert result is item

@pytest.mark.asyncio
async def test_update_item_data_not_found():
    repo = AsyncMock()
    item = MagicMock()
    repo.update_item.return_value = None

    with pytest.raises(ItemNotFound):
        await ItemApplications.update_item_data(item, repo)

    repo.rollback.assert_awaited_once()

@pytest.mark.asyncio
async def test_delete_item_success():
    repo = AsyncMock()
    item_id = uuid4()
    repo.delete_item_by_id.return_value = True

    result = await ItemApplications.delete_item(item_id, repo)

    repo.delete_item_by_id.assert_awaited_once_with(item_id=item_id)
    repo.commit.assert_awaited_once()
    assert result is True

@pytest.mark.asyncio
async def test_delete_item_not_found():
    repo = AsyncMock()
    item_id = uuid4()
    repo.delete_item_by_id.return_value = None

    with pytest.raises(ItemNotFound):
        await ItemApplications.delete_item(item_id, repo)

    repo.rollback.assert_awaited_once()
