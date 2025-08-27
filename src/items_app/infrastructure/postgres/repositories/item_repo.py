from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from items_app.infrastructure.postgres.models import Item
from typing import List, Optional
import logging


logger = logging.getLogger(__name__)


class ItemRepo:
    def __init__(self, async_session: AsyncSession):
        self._session = async_session

    async def add_item(self, item_data: Item) -> Item | None:
        try:
            self._session.add(item_data)
            return item_data
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Error of adding item: {e}")
            return None

    async def get_item_by_id(self, item_id: UUID) -> Item | None:
        try:
            stmt = select(Item).where(Item.id == item_id)
            cursor = await self._session.execute(stmt)
            result = cursor.scalar_one_or_none()
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error of getting item: {e}")
            return None

    async def get_items_by_ids(self, item_ids: List[UUID]) -> List[Item] | None:
        try:
            stmt = select(Item).where(Item.id.in_(item_ids))
            cursor = await self._session.execute(stmt)
            result = list(cursor.scalars().all())
            return result or None
        except SQLAlchemyError as e:
            logger.error(f"Error of getting items by ids: {e}")
            return None

    async def get_items_by_company_id(self, company_id: UUID) -> List[Item] | None:
        try:
            stmt = select(Item).where(Item.company_id == company_id)
            cursor = await self._session.execute(stmt)
            result = list(cursor.scalars().all())
            return result or None
        except SQLAlchemyError as e:
            logger.error(f"Error of getting items by company id: {e}")
            return None

    async def get_items(
        self, offset: Optional[int] = 0, limit: Optional[int] = 10
    ) -> List[Item] | None:
        try:
            stmt = select(Item).offset(offset).limit(limit)
            cursor = await self._session.execute(stmt)
            result = list(cursor.scalars().all())
            return result or None
        except SQLAlchemyError as e:
            logger.error(f"Error of getting items: {e}")
            return None

    async def update_item(self, updated_item_data: Item) -> Item | None:
        try:
            current_item = await self.get_item_by_id(updated_item_data.id)
            if not current_item:
                return None
            else:
                current_item.title = updated_item_data.title
                current_item.price = updated_item_data.price
                return current_item
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Error of updating item: {e}")
            return None

    async def delete_item_by_id(self, item_id: UUID) -> bool | None:
        try:
            current_item = await self.get_item_by_id(item_id)
            if not current_item:
                return None
            else:
                stmt = delete(Item).where(Item.id == item_id)
                await self._session.execute(stmt)
                return True
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Error of deleting item: {e}")
            return None

    async def delete_items_by_ids(self, item_ids: List[UUID]) -> int | None:
        try:
            stmt = delete(Item).where(Item.id.in_(item_ids))
            result = await self._session.execute(stmt)
            return result.rowcount or None
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Error of deleting items: {e}")
            return None

    async def commit(self) -> None:
        try:
            await self._session.commit()
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Error of commiting: {e}")

    async def rollback(self) -> None:
        await self._session.rollback()
