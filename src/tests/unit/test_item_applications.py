import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from items_app.application.items_applications.items_applications_service import ItemsApplicationsService
from items_app.application.items_applications.items_applications_exceptions import ItemNotFound

@pytest.mark.asyncio
async def test_create_item_success():
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    item = MagicMock()
    repo.add_item.return_value = item

    result = await service.create_item(item)

    repo.add_item.assert_awaited_once_with(item_data=item)
    repo.commit.assert_awaited_once()
    assert result is item

@pytest.mark.asyncio
async def test_create_item_failure_rolls_back():
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    item = MagicMock()
    repo.add_item.side_effect = Exception("DB error")

    with pytest.raises(Exception):
        await service.create_item(item)

    repo.rollback.assert_awaited_once()
    repo.commit.assert_not_called()

@pytest.mark.asyncio
async def test_fetch_item_by_id_found():
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    item_id = uuid4()
    fake_item = MagicMock()
    repo.get_item_by_id.return_value = fake_item

    result = await service.fetch_item_by_id(item_id)

    repo.get_item_by_id.assert_awaited_once_with(item_id=item_id)
    assert result is fake_item

@pytest.mark.asyncio
async def test_fetch_item_by_id_not_found():
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    item_id = uuid4()
    repo.get_item_by_id.return_value = None

    with pytest.raises(ItemNotFound):
        await service.fetch_item_by_id(item_id)

@pytest.mark.asyncio
async def test_fetch_items_by_ids_all_found():
    ids = [uuid4(), uuid4()]
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    fake_items = [MagicMock(id=ids[0]), MagicMock(id=ids[1])]
    repo.get_items_by_ids.return_value = fake_items

    result = await service.fetch_items_by_ids(ids)

    assert result == fake_items
    repo.get_items_by_ids.assert_awaited_once_with(item_ids=ids)

@pytest.mark.asyncio
async def test_fetch_items_by_ids_none_found_raises():
    ids = [uuid4(), uuid4()]
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    repo.get_items_by_ids.return_value = []

    with pytest.raises(ItemNotFound) as exc:
        await service.fetch_items_by_ids(ids)
    assert "No items found" in str(exc.value)

@pytest.mark.asyncio
async def test_fetch_items_by_ids_partial_found_raises():
    ids = [uuid4(), uuid4()]
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    found_items = [MagicMock(id=ids[0])]
    repo.get_items_by_ids.return_value = found_items

    with pytest.raises(ItemNotFound) as exc:
        await service.fetch_items_by_ids(ids)
    assert str(ids[1]) in str(exc.value)

@pytest.mark.asyncio
async def test_fetch_items_by_ids_empty_input():
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    repo.get_items_by_ids.return_value = []

    with pytest.raises(ItemNotFound):
        await service.fetch_items_by_ids([])

@pytest.mark.asyncio
async def test_fetch_items_of_company_by_company_id_found():
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    company_id = uuid4()
    fake_items = [MagicMock(), MagicMock()]
    repo.get_items_by_company_id.return_value = fake_items

    result = await service.fetch_items_of_company_by_company_id(company_id)

    repo.get_items_by_company_id.assert_awaited_once_with(company_id=company_id)
    assert result == fake_items

@pytest.mark.asyncio
async def test_fetch_items_of_company_by_company_id_not_found():
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    company_id = uuid4()
    repo.get_items_by_company_id.return_value = None

    with pytest.raises(ItemNotFound):
        await service.fetch_items_of_company_by_company_id(company_id)

@pytest.mark.asyncio
async def test_fetch_all_items_success():
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    items = [MagicMock(), MagicMock()]
    repo.get_items.return_value = items

    result = await service.fetch_all_items(0, 10)

    repo.get_items.assert_awaited_once_with(0, 10)
    assert result == items

@pytest.mark.asyncio
async def test_update_item_data_success():
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    item = MagicMock()
    repo.update_item.return_value = item

    result = await service.update_item_data(item)

    repo.update_item.assert_awaited_once_with(updated_item_data=item)
    repo.commit.assert_awaited_once()
    assert result is item

@pytest.mark.asyncio
async def test_update_item_data_not_found():
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    item = MagicMock()
    repo.update_item.return_value = None

    with pytest.raises(ItemNotFound):
        await service.update_item_data(item)

    repo.rollback.assert_awaited_once()

@pytest.mark.asyncio
async def test_delete_item_success():
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    item_id = uuid4()
    repo.delete_item_by_id.return_value = True

    result = await service.delete_item(item_id)

    repo.delete_item_by_id.assert_awaited_once_with(item_id=item_id)
    repo.commit.assert_awaited_once()
    assert result is True

@pytest.mark.asyncio
async def test_delete_item_not_found():
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    item_id = uuid4()
    repo.delete_item_by_id.return_value = None

    with pytest.raises(ItemNotFound):
        await service.delete_item(item_id)

    repo.rollback.assert_awaited_once()

@pytest.mark.asyncio
async def test_delete_items_success():
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    item_ids = [uuid4(), uuid4(), uuid4()]
    repo.get_items_by_ids.return_value = [MagicMock(id=item_id) for item_id in item_ids]
    repo.delete_items_by_ids.return_value = True

    result = await service.delete_items(item_ids)

    repo.delete_items_by_ids.assert_awaited_once_with(item_ids=item_ids)
    repo.commit.assert_awaited_once()
    assert result is True

@pytest.mark.asyncio
async def test_delete_items_not_found():
    repo = AsyncMock()
    service = ItemsApplicationsService(repo)
    item_ids = [uuid4(), uuid4(), uuid4()]
    repo.get_items_by_ids.return_value = []
    repo.delete_items_by_ids.return_value = None

    with pytest.raises(ItemNotFound):
        await service.delete_items(item_ids)

    repo.rollback.assert_awaited_once()
