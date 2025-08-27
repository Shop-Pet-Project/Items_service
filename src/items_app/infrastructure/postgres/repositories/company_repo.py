from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from items_app.infrastructure.postgres.models import Item, Company
from typing import List, Optional
import logging


logger = logging.getLogger(__name__)


class CompanyRepo:
    def __init__(self, async_session: AsyncSession):
        self._session = async_session

    async def add_company(self, company_data: Company) -> Company | None:
        try:
            self._session.add(company_data)
            return company_data
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Error of adding company: {e}")
            return None

    async def get_company_by_id(self, company_id: UUID) -> Company | None:
        try:
            stmt = select(Company).where(Company.id == company_id)
            cursor = await self._session.execute(stmt)
            result = cursor.scalar_one_or_none()
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error of getting company: {e}")
            return None

    async def get_all_companies(
        self, offset: Optional[int] = 0, limit: Optional[int] = 10
    ) -> List[Company] | None:
        try:
            stmt = select(Company).offset(offset).limit(limit)
            cursor = await self._session.execute(stmt)
            result = list(cursor.scalars().all())
            return result or None
        except SQLAlchemyError as e:
            logger.error(f"Error of getting companies: {e}")
            return None

    async def update_company_data(
        self, updated_company_data: Company
    ) -> Company | None:
        try:
            current_company = await self.get_company_by_id(updated_company_data.id)
            if not current_company:
                return None
            else:
                current_company.name = updated_company_data.name
                return current_company
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Error of updating company: {e}")
            return None

    async def remove_company_by_id(self, company_id: UUID) -> bool | None:
        try:
            current_company = await self.get_company_by_id(company_id)
            if not current_company:
                return None
            else:
                del_items_stmt = delete(Item).where(Item.company_id == company_id)
                await self._session.execute(del_items_stmt)

                del_company_stmt = delete(Company).where(Company.id == company_id)
                await self._session.execute(del_company_stmt)
                return True
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Error of deleting company: {e}")
            return None

    async def commit(self) -> None:
        try:
            await self._session.commit()
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Error of commiting: {e}")

    async def rollback(self) -> None:
        await self._session.rollback()
