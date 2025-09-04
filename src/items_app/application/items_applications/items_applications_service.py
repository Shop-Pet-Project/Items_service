import logging
from uuid import UUID
from typing import List, Optional
from items_app.application.items_applications.items_applications_exceptions import (
    ItemNotFound, NoAccessToItem
)
from items_app.infrastructure.postgres.models import Item
from items_app.infrastructure.postgres.repositories.item_repo import ItemRepo
from items_app.infrastructure.redis.cache.async_cache_manager import AsyncCacheManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ItemsApplicationsService:
    def __init__(self, item_repo: ItemRepo, cache: AsyncCacheManager):
        self.item_repo = item_repo
        self.cache = cache

    async def _invalidate_items_cache(self):
        invalidate_cache_key = self.cache.generate_key("items", "*")
        await self.cache.delete_pattern(invalidate_cache_key)

    async def create_item(self, new_item: Item) -> Optional[Item]:
        try:
            created_item = await self.item_repo.add_item(item_data=new_item)
            await self.item_repo.commit()
            await self._invalidate_items_cache()
            return created_item
        except Exception as e:
            await self.item_repo.rollback()
            logger.error(f"Error of creating item: {e}")
            raise

    async def fetch_item_by_id(self, item_id: UUID, company_id: UUID) -> Item | None:
        try:
            cache_key = self.cache.generate_key("items", f"company_id={company_id}", f"item_id={item_id}")
            if cache_value := await self.cache.get(cache_key):
                return cache_value
            response = await self.item_repo.get_item_by_id(item_id=item_id)
            if not response:
                raise ItemNotFound(f"Item with item_id={item_id} not found")
            if response.company_id != company_id:
                raise NoAccessToItem(f"Comapany with ID {company_id} do not have access for item with ID {item_id}")
            await self.cache.set(cache_key, response)
            return response
        except Exception as e:
            logger.error(f"Error of getting item by id: {e}")
            raise

    async def get_missing_ids(
        self, existing_items: Optional[List[Item]], item_ids: List[UUID]
    ) -> List[str]:
        try:
            existing_items_set = (
                {item.id for item in existing_items} if existing_items else set()
            )
            missing_ids = [
                str(item_id)
                for item_id in item_ids
                if item_id not in existing_items_set
            ]
            return missing_ids
        except Exception as e:
            logger.error(f"Error of getting existing and missing ids: {e}")
            raise

    async def fetch_items_by_ids(self, item_ids: List[UUID], company_id: UUID) -> List[Item] | None:
        try:
            items_ids_for_cache = ",".join(sorted(str(i) for i in item_ids))
            cache_key = self.cache.generate_key("items", f"company_id={company_id}", f"items_ids={items_ids_for_cache}")
            if cache_value := await self.cache.get(cache_key):
                return cache_value
            response = await self.item_repo.get_items_by_ids(item_ids=item_ids)
            if not response or len(response) != len(item_ids):
                missing_ids = await self.get_missing_ids(response, item_ids)
                raise ItemNotFound(f"No items found with IDs {', '.join(missing_ids)}")
            for item in response:
                if item.company_id != company_id:
                    raise NoAccessToItem("You do not have access to some items")
            await self.cache.set(cache_key, response)
            return response
        except Exception as e:
            logger.error(f"Error of getting items by ids: {e}")
            raise

    async def fetch_items_of_company_by_company_id(
        self, company_id: UUID
    ) -> List[Item] | None:
        try:
            cache_key = self.cache.generate_key("items", f"company_id={company_id}", "all")
            if cache_value := await self.cache.get(cache_key):
                return cache_value

            response = await self.item_repo.get_items_by_company_id(
                company_id=company_id
            )
            if not response:
                raise ItemNotFound(
                    f"No items found for company with company_id={company_id}"
                )
            await self.cache.set(cache_key, response)
            return response
        except Exception as e:
            logger.error(f"Error of getting items by company id: {e}")
            raise

    async def fetch_all_items(
        self, offset: Optional[int], limit: Optional[int]
    ) -> List[Item] | None:
        try:
            cache_key = self.cache.generate_key("items", "all", f"offset={offset}", f"limit={limit}")
            if cache_value := await self.cache.get(cache_key):
                return cache_value
            
            response = await self.item_repo.get_items(offset, limit)
            await self.cache.set(cache_key, response)
            return response
        except Exception as e:
            logger.error(f"Error of getting all items: {e}")
            raise

    async def update_item_data(self, update_item: Item) -> Item | None:
        try:
            response = await self.item_repo.update_item(updated_item_data=update_item)
            if not response:
                raise ItemNotFound(f"No such item with item_id={update_item.id}")
            await self.item_repo.commit()
            await self._invalidate_items_cache()
            return response
        except Exception as e:
            await self.item_repo.rollback()
            logger.error(f"Error of updating item: {e}")
            raise

    async def delete_item(self, item_id: UUID, company_id: UUID) -> bool | None:
        try:
            response = await self.item_repo.delete_item_by_id(item_id=item_id)
            if not response:
                raise ItemNotFound(f"No such item with item_id={item_id}")
            await self.item_repo.commit()
            await self._invalidate_items_cache()
            return True
        except Exception as e:
            await self.item_repo.rollback()
            logger.error(f"Error of deleting item: {e}")
            raise

    async def delete_items(self, item_ids: List[UUID], company_id: UUID) -> bool | None:
        try:
            existing_items = await self.item_repo.get_items_by_ids(item_ids=item_ids)
            if not existing_items or len(existing_items) != len(item_ids):
                missing_ids = await self.get_missing_ids(existing_items, item_ids)
                raise ItemNotFound(f"No items found with IDs {', '.join(missing_ids)}")

            await self.item_repo.delete_items_by_ids(item_ids=item_ids)
            await self.item_repo.commit()
            await self._invalidate_items_cache()
            return True
        except Exception as e:
            await self.item_repo.rollback()
            logger.error(f"Error of deleting items: {e}")
            raise
