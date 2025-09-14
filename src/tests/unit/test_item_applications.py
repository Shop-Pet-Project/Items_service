import pytest
from uuid import uuid4
from unittest.mock import MagicMock
from tests.unit.fixtures import mock_repo, mock_cache
from items_app.application.items_applications.items_applications_service import (
    ItemsApplicationsService,
)
from items_app.application.items_applications.items_applications_exceptions import (
    ItemNotFound,
)


@pytest.fixture
def service(mock_repo, mock_cache):
    return ItemsApplicationsService(mock_repo, mock_cache)


@pytest.mark.asyncio
async def test_create_item_success(service, mock_repo):
    item = MagicMock()
    mock_repo.add_item.return_value = item

    result = await service.create_item(item)

    mock_repo.add_item.assert_awaited_once_with(item_data=item)
    mock_repo.commit.assert_awaited_once()
    assert result is item


@pytest.mark.asyncio
async def test_create_item_failure_rolls_back(service, mock_repo):
    item = MagicMock()
    mock_repo.add_item.side_effect = Exception("DB error")

    with pytest.raises(Exception):
        await service.create_item(item)

    mock_repo.rollback.assert_awaited_once()
    mock_repo.commit.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_item_by_id_found(service, mock_repo, mock_cache):
    item_id = uuid4()
    company_id = uuid4()
    fake_item = MagicMock()
    mock_cache.get.return_value = None
    mock_repo.get_item_by_id.return_value = fake_item
    fake_item.company_id = company_id

    result = await service.fetch_item_by_id(item_id, company_id)

    mock_repo.get_item_by_id.assert_awaited_once_with(item_id=item_id)
    mock_cache.set.assert_awaited_once()
    assert result is fake_item


@pytest.mark.asyncio
async def test_fetch_item_by_id_not_found(service, mock_repo, mock_cache):
    item_id = uuid4()
    company_id = uuid4()
    mock_cache.get.return_value = None
    mock_repo.get_item_by_id.return_value = None

    with pytest.raises(ItemNotFound):
        await service.fetch_item_by_id(item_id, company_id)


@pytest.mark.asyncio
async def test_fetch_items_by_ids_all_found(service, mock_repo, mock_cache):
    ids = [uuid4(), uuid4()]
    company_id = uuid4()
    fake_items = [
        MagicMock(id=ids[0], company_id=company_id),
        MagicMock(id=ids[1], company_id=company_id),
    ]
    mock_cache.get.return_value = None
    mock_repo.get_items_by_ids.return_value = fake_items

    result = await service.fetch_items_by_ids(ids, company_id)

    assert result == fake_items
    mock_repo.get_items_by_ids.assert_awaited_once_with(item_ids=ids)
    mock_cache.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_items_by_ids_none_found_raises(service, mock_repo, mock_cache):
    ids = [uuid4(), uuid4()]
    company_id = uuid4()
    mock_cache.get.return_value = None
    mock_repo.get_items_by_ids.return_value = []

    with pytest.raises(ItemNotFound) as exc:
        await service.fetch_items_by_ids(ids, company_id)
    assert "No items found" in str(exc.value)


@pytest.mark.asyncio
async def test_fetch_items_by_ids_partial_found_raises(service, mock_repo, mock_cache):
    ids = [uuid4(), uuid4()]
    company_id = uuid4()
    found_items = [MagicMock(id=ids[0], company_id=company_id)]
    mock_cache.get.return_value = None
    mock_repo.get_items_by_ids.return_value = found_items

    with pytest.raises(ItemNotFound) as exc:
        await service.fetch_items_by_ids(ids, company_id)
    assert str(ids[1]) in str(exc.value)


@pytest.mark.asyncio
async def test_fetch_items_by_ids_empty_input(service, mock_repo, mock_cache):
    company_id = uuid4()
    mock_cache.get.return_value = None
    mock_repo.get_items_by_ids.return_value = []

    with pytest.raises(ItemNotFound):
        await service.fetch_items_by_ids([], company_id)


@pytest.mark.asyncio
async def test_fetch_items_of_company_by_company_id_found(
    service, mock_repo, mock_cache
):
    company_id = uuid4()
    fake_items = [MagicMock(), MagicMock()]
    mock_cache.get.return_value = None
    mock_repo.get_items_by_company_id.return_value = fake_items

    result = await service.fetch_items_of_company_by_company_id(company_id)

    mock_repo.get_items_by_company_id.assert_awaited_once_with(company_id=company_id)
    mock_cache.set.assert_awaited_once()
    assert result == fake_items


@pytest.mark.asyncio
async def test_fetch_items_of_company_by_company_id_not_found(
    service, mock_repo, mock_cache
):
    company_id = uuid4()
    mock_cache.get.return_value = None
    mock_repo.get_items_by_company_id.return_value = None

    with pytest.raises(ItemNotFound):
        await service.fetch_items_of_company_by_company_id(company_id)


@pytest.mark.asyncio
async def test_fetch_all_items_success(service, mock_repo, mock_cache):
    items = [MagicMock(), MagicMock()]
    mock_cache.get.return_value = None
    mock_repo.get_items.return_value = items

    result = await service.fetch_all_items(0, 10)

    mock_repo.get_items.assert_awaited_once_with(0, 10)
    mock_cache.set.assert_awaited_once()
    assert result == items


@pytest.mark.asyncio
async def test_update_item_data_success(service, mock_repo):
    item = MagicMock()
    mock_repo.update_item.return_value = item

    result = await service.update_item_data(item)

    mock_repo.update_item.assert_awaited_once_with(updated_item_data=item)
    mock_repo.commit.assert_awaited_once()
    assert result is item


@pytest.mark.asyncio
async def test_update_item_data_not_found(service, mock_repo):
    item = MagicMock()
    mock_repo.update_item.return_value = None

    with pytest.raises(ItemNotFound):
        await service.update_item_data(item)

    mock_repo.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_item_success(service, mock_repo):
    item_id = uuid4()
    company_id = uuid4()
    mock_repo.delete_item_by_id.return_value = True

    result = await service.delete_item(item_id, company_id)

    mock_repo.delete_item_by_id.assert_awaited_once_with(item_id=item_id)
    mock_repo.commit.assert_awaited_once()
    assert result is True


@pytest.mark.asyncio
async def test_delete_item_not_found(service, mock_repo):
    item_id = uuid4()
    company_id = uuid4()
    mock_repo.delete_item_by_id.return_value = None

    with pytest.raises(ItemNotFound):
        await service.delete_item(item_id, company_id)

    mock_repo.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_items_success(service, mock_repo):
    item_ids = [uuid4(), uuid4(), uuid4()]
    company_id = uuid4()
    mock_repo.get_items_by_ids.return_value = [
        MagicMock(id=item_id, company_id=company_id) for item_id in item_ids
    ]
    mock_repo.delete_items_by_ids.return_value = True

    result = await service.delete_items(item_ids, company_id)

    mock_repo.delete_items_by_ids.assert_awaited_once_with(item_ids=item_ids)
    mock_repo.commit.assert_awaited_once()
    assert result is True


@pytest.mark.asyncio
async def test_delete_items_not_found(service, mock_repo):
    item_ids = [uuid4(), uuid4(), uuid4()]
    company_id = uuid4()
    mock_repo.get_items_by_ids.return_value = []
    mock_repo.delete_items_by_ids.return_value = None

    with pytest.raises(ItemNotFound):
        await service.delete_items(item_ids, company_id)

    mock_repo.rollback.assert_awaited_once()
