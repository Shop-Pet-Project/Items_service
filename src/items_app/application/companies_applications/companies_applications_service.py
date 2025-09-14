import logging
from uuid import UUID
from typing import List, Optional
from items_app.application.companies_applications.companies_applications_exceptions import (
    CompanyNotFound,
)
from items_app.infrastructure.postgres.models import Company
from items_app.infrastructure.postgres.repositories.company_repo import CompanyRepo
from items_app.infrastructure.redis.cache.async_cache_manager import AsyncCacheManager

logger = logging.getLogger(__name__)


class CompaniesApplicationsService:
    def __init__(self, company_repo: CompanyRepo, cache: AsyncCacheManager):
        self.company_repo = company_repo
        self.cache = cache

    async def _invalidate_companies_cache(self):
        invalidate_cache_key = self.cache.generate_key("companies", "*")
        await self.cache.delete_pattern(invalidate_cache_key)

    async def _invalidate_companies_and_items_cache(self):
        invalidate_companies_cache_key = self.cache.generate_key("companies", "*")
        invalidate_items_cache_key = self.cache.generate_key("items", "*")
        await self.cache.delete_pattern(
            invalidate_companies_cache_key, invalidate_items_cache_key
        )

    async def create_company(self, new_company: Company) -> Optional[Company]:
        try:
            created_company = await self.company_repo.add_company(
                company_data=new_company
            )
            await self.company_repo.commit()
            await self._invalidate_companies_cache()
            return created_company
        except Exception as e:
            await self.company_repo.rollback()
            logger.error(f"Error of creating company: {e}")
            raise

    async def fetch_company_by_id(self, company_id: UUID) -> Company | None:
        try:
            cache_key = self.cache.generate_key("companies", f"company_id={company_id}")
            if cache_value := await self.cache.get(cache_key):
                return cache_value

            response = await self.company_repo.get_company_by_id(company_id=company_id)
            if not response:
                raise CompanyNotFound(f"Company with company_id={company_id} not found")
            await self.cache.set(cache_key, response)
            return response
        except Exception as e:
            logger.error(f"Error of fetching company by id: {e}")
            raise

    async def fetch_all_companies(
        self, offset: Optional[int], limit: Optional[int]
    ) -> List[Company] | None:
        try:
            cache_key = self.cache.generate_key(
                "companies", "all", f"offset={offset}", f"limit={limit}"
            )
            if cache_value := await self.cache.get(cache_key):
                return cache_value

            response = await self.company_repo.get_all_companies(offset, limit)
            await self.cache.set(cache_key, response)
            return response
        except Exception as e:
            logger.error(f"Error of getting all companies: {e}")
            raise

    async def update_company_data(self, update_company: Company) -> Company | None:
        try:
            response = await self.company_repo.update_company_data(
                updated_company_data=update_company
            )
            if not response:
                raise CompanyNotFound(
                    f"No such company with company_id={update_company.id}"
                )
            await self.company_repo.commit()
            await self._invalidate_companies_cache()
            return response
        except Exception as e:
            await self.company_repo.rollback()
            logger.error(f"Error of updating company: {e}")
            raise

    async def delete_company(self, company_id: UUID) -> bool | None:
        try:
            response = await self.company_repo.remove_company_by_id(
                company_id=company_id
            )
            if not response:
                raise CompanyNotFound(f"No such company with company_id={company_id}")
            await self.company_repo.commit()
            await self._invalidate_companies_and_items_cache()
            return True
        except Exception as e:
            await self.company_repo.rollback()
            logger.error(f"Error of deleting company: {e}")
            raise
