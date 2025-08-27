import logging
from uuid import UUID
from typing import List, Optional
from items_app.application.companies_applications.companies_applications_exceptions import CompanyNotFound
from items_app.infrastructure.postgres.models import Company
from items_app.infrastructure.postgres.repository import CompanyRepo

logger = logging.getLogger(__name__)


class CompaniesApplicationsService:
    def __init__(self, company_repo: CompanyRepo):
        self.company_repo = company_repo

    async def create_company(self, new_company: Company) -> Optional[Company]:
        try:
            created_company = await self.company_repo.add_company(company_data=new_company)
            await self.company_repo.commit()
            return created_company
        except Exception as e:
            await self.company_repo.rollback()
            logger.error(f"Error of creating company: {e}")
            raise

    async def fetch_company_by_id(self, company_id: UUID) -> Company | None:
        try:
            response = await self.company_repo.get_company_by_id(company_id=company_id)
            if not response:
                raise CompanyNotFound(f"Company with company_id={company_id} not found")
            else:
                return response
        except Exception as e:
            logger.error(f"Error of getting company by id: {e}")
            raise

    async def fetch_all_companies(self, offset: Optional[int], limit: Optional[int]) -> List[Company] | None:
        try:
            response = await self.company_repo.get_all_companies(offset, limit)
            return response
        except Exception as e:
            logger.error(f"Error of getting all companies: {e}")
            raise

    async def update_company_data(self, update_company: Company) -> Company | None:
        try:
            response = await self.company_repo.update_company_data(updated_company_data=update_company)
            if not response:
                raise CompanyNotFound(f"No such company with company_id={update_company.id}")
            else:
                await self.company_repo.commit()
                return response
        except Exception as e:
            await self.company_repo.rollback()
            logger.error(f"Error of updating company: {e}")
            raise

    async def delete_company(self, company_id: UUID) -> bool | None:
        try:
            response = await self.company_repo.remove_company_by_id(company_id=company_id)
            if not response:
                raise CompanyNotFound(f"No such company with company_id={company_id}")
            else:
                await self.company_repo.commit()
                return True
        except Exception as e:
            await self.company_repo.rollback()
            logger.error(f"Error of deleting company: {e}")
            raise
