import pytest
from uuid import uuid4
from unittest.mock import MagicMock
from tests.unit.fixtures import mock_repo, mock_cache
from items_app.application.companies_applications.companies_applications_service import (
    CompaniesApplicationsService,
)
from items_app.application.companies_applications.companies_applications_exceptions import (
    CompanyNotFound,
)


@pytest.fixture
def service(mock_repo, mock_cache):
    return CompaniesApplicationsService(company_repo=mock_repo, cache=mock_cache)

@pytest.mark.asyncio
async def test_create_company_success(service, mock_repo):
    company = MagicMock()
    mock_repo.add_company.return_value = company

    result = await service.create_company(company)

    mock_repo.add_company.assert_awaited_once_with(company_data=company)
    mock_repo.commit.assert_awaited_once()
    assert result is company

@pytest.mark.asyncio
async def test_fetch_company_by_id_found(service, mock_repo, mock_cache):
    company_id = uuid4()
    fake_company = MagicMock()
    mock_cache.get.return_value = None
    mock_repo.get_company_by_id.return_value = fake_company

    result = await service.fetch_company_by_id(company_id)

    mock_repo.get_company_by_id.assert_awaited_once_with(company_id=company_id)
    mock_cache.set.assert_awaited_once()
    assert result is fake_company

@pytest.mark.asyncio
async def test_fetch_company_by_id_not_found(service, mock_repo, mock_cache):
    company_id = uuid4()
    mock_cache.get.return_value = None
    mock_repo.get_company_by_id.return_value = None

    with pytest.raises(CompanyNotFound):
        await service.fetch_company_by_id(company_id)

@pytest.mark.asyncio
async def test_fetch_all_companies_success(service, mock_repo, mock_cache):
    companies = [MagicMock(), MagicMock()]
    mock_cache.get.return_value = None
    mock_repo.get_all_companies.return_value = companies

    result = await service.fetch_all_companies(0, 10)

    mock_repo.get_all_companies.assert_awaited_once_with(0, 10)
    mock_cache.set.assert_awaited_once()
    assert result == companies

@pytest.mark.asyncio
async def test_fetch_all_companies_empty(service, mock_repo, mock_cache):
    mock_cache.get.return_value = None
    mock_repo.get_all_companies.return_value = []

    result = await service.fetch_all_companies(0, 10)

    mock_repo.get_all_companies.assert_awaited_once_with(0, 10)
    mock_cache.set.assert_awaited_once()
    assert result == []

@pytest.mark.asyncio
async def test_update_company_data_success(service, mock_repo):
    company = MagicMock()
    mock_repo.update_company_data.return_value = company

    result = await service.update_company_data(company)

    mock_repo.update_company_data.assert_awaited_once_with(updated_company_data=company)
    mock_repo.commit.assert_awaited_once()
    assert result is company

@pytest.mark.asyncio
async def test_update_company_data_not_found(service, mock_repo):
    company = MagicMock()
    mock_repo.update_company_data.return_value = None

    with pytest.raises(CompanyNotFound):
        await service.update_company_data(company)

    mock_repo.rollback.assert_awaited_once()

@pytest.mark.asyncio
async def test_delete_company_success(service, mock_repo):
    company_id = uuid4()
    mock_repo.remove_company_by_id.return_value = True

    result = await service.delete_company(company_id)

    mock_repo.remove_company_by_id.assert_awaited_once_with(company_id=company_id)
    mock_repo.commit.assert_awaited_once()
    assert result is True

@pytest.mark.asyncio
async def test_delete_company_not_found(service, mock_repo):
    company_id = uuid4()
    mock_repo.remove_company_by_id.return_value = None

    with pytest.raises(CompanyNotFound):
        await service.delete_company(company_id)

    mock_repo.rollback.assert_awaited_once()
