import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from items_app.application.application import ItemApplications, CompanyApplications
from items_app.application.application_exceptions import ItemNotFound, CompanyNotFound

""" Тесты для ItemsApplications. """


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
async def test_fetch_items_by_ids_all_found():
    ids = [uuid4(), uuid4()]
    mock_repo = AsyncMock()
    fake_items = [
        MagicMock(id=ids[0], title="Item1", price=10.0),
        MagicMock(id=ids[1], title="Item2", price=20.0),
    ]
    mock_repo.get_items_by_ids.return_value = fake_items

    result = await ItemApplications.fetch_items_by_ids(ids, mock_repo)

    assert result == fake_items
    mock_repo.get_items_by_ids.assert_awaited_once_with(item_ids=ids)


@pytest.mark.asyncio
async def test_fetch_items_by_ids_none_found_raises():
    ids = [uuid4(), uuid4()]
    mock_repo = AsyncMock()
    mock_repo.get_items_by_ids.return_value = []

    with pytest.raises(ItemNotFound) as exc:
        await ItemApplications.fetch_items_by_ids(ids, mock_repo)
    assert "No items found" in str(exc.value)


@pytest.mark.asyncio
async def test_fetch_items_by_ids_partial_found_raises():
    ids = [uuid4(), uuid4()]
    mock_repo = AsyncMock()
    found_items = [MagicMock(id=ids[0], title="OnlyOne", price=5.0)]
    mock_repo.get_items_by_ids.return_value = found_items
    missing_ids = [str(ids[1])]
    ItemApplications.get_missing_ids = AsyncMock(return_value=missing_ids)

    with pytest.raises(ItemNotFound) as exc:
        await ItemApplications.fetch_items_by_ids(ids, mock_repo)
    assert str(ids[1]) in str(exc.value)


@pytest.mark.asyncio
async def test_fetch_items_by_ids_empty_input():
    mock_repo = AsyncMock()
    mock_repo.get_items_by_ids.return_value = []

    with pytest.raises(ItemNotFound):
        await ItemApplications.fetch_items_by_ids([], mock_repo)


@pytest.mark.asyncio
async def test_fetch_items_of_company_by_company_id_found():
    repo = AsyncMock()
    company_id = uuid4()
    fake_items = [MagicMock(), MagicMock()]
    repo.get_items_by_company_id.return_value = fake_items

    result = await ItemApplications.fetch_items_of_company_by_company_id(
        company_id, repo
    )

    repo.get_items_by_company_id.assert_awaited_once_with(company_id=company_id)
    assert result == fake_items


@pytest.mark.asyncio
async def test_fetch_items_of_company_by_company_id_not_found():
    repo = AsyncMock()
    company_id = uuid4()
    repo.get_items_by_company_id.return_value = None

    with pytest.raises(ItemNotFound):
        await ItemApplications.fetch_items_of_company_by_company_id(company_id, repo)


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


@pytest.mark.asyncio
async def test_delete_items_success():
    repo = AsyncMock()
    item_ids = [uuid4(), uuid4(), uuid4()]
    repo.get_items_by_ids.return_value = [MagicMock(id=item_id) for item_id in item_ids]
    repo.delete_items_by_ids.return_value = True

    result = await ItemApplications.delete_items(item_ids, repo)

    repo.delete_items_by_ids.assert_awaited_once_with(item_ids=item_ids)
    repo.commit.assert_awaited_once()
    assert result is True


@pytest.mark.asyncio
async def test_delete_items_not_found():
    repo = AsyncMock()
    item_ids = [uuid4(), uuid4(), uuid4()]
    repo.delete_items_by_ids.return_value = None

    with pytest.raises(ItemNotFound):
        await ItemApplications.delete_items(item_ids, repo)

    repo.rollback.assert_awaited_once()


""" Тесты для CompanyApplications. """


@pytest.mark.asyncio
async def test_create_company_success():
    repo = AsyncMock()
    company = MagicMock()
    repo.add_company.return_value = company

    result = await CompanyApplications.create_company(company, repo)

    repo.add_company.assert_awaited_once_with(company_data=company)
    repo.commit.assert_awaited_once()
    assert result is company


@pytest.mark.asyncio
async def test_fetch_company_by_id_found():
    repo = AsyncMock()
    company_id = uuid4()
    fake_company = MagicMock()
    repo.get_company_by_id.return_value = fake_company

    result = await CompanyApplications.fetch_company_by_id(company_id, repo)

    repo.get_company_by_id.assert_awaited_once_with(company_id=company_id)
    assert result is fake_company


@pytest.mark.asyncio
async def test_fetch_company_by_id_not_found():
    repo = AsyncMock()
    company_id = uuid4()
    repo.get_company_by_id.return_value = None

    with pytest.raises(CompanyNotFound):
        await CompanyApplications.fetch_company_by_id(company_id, repo)


@pytest.mark.asyncio
async def test_fetch_all_companies_success():
    repo = AsyncMock()
    companies = [MagicMock(), MagicMock()]
    repo.get_companies.return_value = companies

    result = await CompanyApplications.fetch_all_companies(0, 10, repo)

    repo.get_companies.assert_awaited_once_with(0, 10)
    assert result == companies


@pytest.mark.asyncio
async def test_fetch_all_companies_empty():
    repo = AsyncMock()
    repo.get_companies.return_value = []

    result = await CompanyApplications.fetch_all_companies(0, 10, repo)

    repo.get_companies.assert_awaited_once_with(0, 10)
    assert result == []


@pytest.mark.asyncio
async def test_update_company_data_success():
    repo = AsyncMock()
    company = MagicMock()
    repo.update_company_data.return_value = company

    result = await CompanyApplications.update_company_data(company, repo)

    repo.update_company_data.assert_awaited_once_with(updated_company_data=company)
    repo.commit.assert_awaited_once()
    assert result is company


@pytest.mark.asyncio
async def test_update_company_data_not_found():
    repo = AsyncMock()
    company = MagicMock()
    repo.update_company_data.return_value = None

    with pytest.raises(CompanyNotFound):
        await CompanyApplications.update_company_data(company, repo)

    repo.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_company_success():
    repo = AsyncMock()
    company_id = uuid4()
    repo.remove_company_by_id.return_value = True

    result = await CompanyApplications.delete_company(company_id, repo)

    repo.remove_company_by_id.assert_awaited_once_with(company_id=company_id)
    repo.commit.assert_awaited_once()
    assert result is True


@pytest.mark.asyncio
async def test_delete_company_not_found():
    repo = AsyncMock()
    company_id = uuid4()
    repo.remove_company_by_id.return_value = None

    with pytest.raises(CompanyNotFound):
        await CompanyApplications.delete_company(company_id, repo)

    repo.rollback.assert_awaited_once()
