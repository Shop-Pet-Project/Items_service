import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from items_app.application.companies_applications.companies_applications_service import CompaniesApplicationsService
from items_app.application.companies_applications.companies_applications_exceptions import CompanyNotFound

@pytest.mark.asyncio
async def test_create_company_success():
    repo = AsyncMock()
    service = CompaniesApplicationsService(company_repo=repo)
    company = MagicMock()
    repo.add_company.return_value = company

    result = await service.create_company(company)

    repo.add_company.assert_awaited_once_with(company_data=company)
    repo.commit.assert_awaited_once()
    assert result is company

@pytest.mark.asyncio
async def test_fetch_company_by_id_found():
    repo = AsyncMock()
    service = CompaniesApplicationsService(company_repo=repo)
    company_id = uuid4()
    fake_company = MagicMock()
    repo.get_company_by_id.return_value = fake_company

    result = await service.fetch_company_by_id(company_id)

    repo.get_company_by_id.assert_awaited_once_with(company_id=company_id)
    assert result is fake_company

@pytest.mark.asyncio
async def test_fetch_company_by_id_not_found():
    repo = AsyncMock()
    service = CompaniesApplicationsService(company_repo=repo)
    company_id = uuid4()
    repo.get_company_by_id.return_value = None

    with pytest.raises(CompanyNotFound):
        await service.fetch_company_by_id(company_id)

@pytest.mark.asyncio
async def test_fetch_all_companies_success():
    repo = AsyncMock()
    service = CompaniesApplicationsService(company_repo=repo)
    companies = [MagicMock(), MagicMock()]
    repo.get_all_companies.return_value = companies

    result = await service.fetch_all_companies(0, 10)

    repo.get_all_companies.assert_awaited_once_with(0, 10)
    assert result == companies

@pytest.mark.asyncio
async def test_fetch_all_companies_empty():
    repo = AsyncMock()
    service = CompaniesApplicationsService(company_repo=repo)
    repo.get_all_companies.return_value = []

    result = await service.fetch_all_companies(0, 10)

    repo.get_all_companies.assert_awaited_once_with(0, 10)
    assert result == []

@pytest.mark.asyncio
async def test_update_company_data_success():
    repo = AsyncMock()
    service = CompaniesApplicationsService(company_repo=repo)
    company = MagicMock()
    repo.update_company_data.return_value = company

    result = await service.update_company_data(company)

    repo.update_company_data.assert_awaited_once_with(updated_company_data=company)
    repo.commit.assert_awaited_once()
    assert result is company

@pytest.mark.asyncio
async def test_update_company_data_not_found():
    repo = AsyncMock()
    service = CompaniesApplicationsService(company_repo=repo)
    company = MagicMock()
    repo.update_company_data.return_value = None

    with pytest.raises(CompanyNotFound):
        await service.update_company_data(company)

    repo.rollback.assert_awaited_once()

@pytest.mark.asyncio
async def test_delete_company_success():
    repo = AsyncMock()
    service = CompaniesApplicationsService(company_repo=repo)
    company_id = uuid4()
    repo.remove_company_by_id.return_value = True

    result = await service.delete_company(company_id)

    repo.remove_company_by_id.assert_awaited_once_with(company_id=company_id)
    repo.commit.assert_awaited_once()
    assert result is True

@pytest.mark.asyncio
async def test_delete_company_not_found():
    repo = AsyncMock()
    service = CompaniesApplicationsService(company_repo=repo)
    company_id = uuid4()
    repo.remove_company_by_id.return_value = None

    with pytest.raises(CompanyNotFound):
        await service.delete_company(company_id)

    repo.rollback.assert_awaited_once()
