import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from items_app.application.application import CompanyApplications
from items_app.application.application_exceptions import CompanyNotFound

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
    repo.get_all_companies.return_value = companies

    result = await CompanyApplications.fetch_all_companies(0, 10, repo)

    repo.get_all_companies.assert_awaited_once_with(0, 10)
    assert result == companies


@pytest.mark.asyncio
async def test_fetch_all_companies_empty():
    repo = AsyncMock()
    repo.get_all_companies.return_value = []

    result = await CompanyApplications.fetch_all_companies(0, 10, repo)

    repo.get_all_companies.assert_awaited_once_with(0, 10)
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
