import logging
from typing import List, Optional
from items_app.application.application_exceptions import ItemNotFound
from items_app.infrastructure.models import Item
from items_app.infrastructure.repository import ItemRepo
from items_app.api.schemas import ItemCreate, ItemResponse


logger = logging.getLogger(__name__)


class ItemApplications:
    @staticmethod
    async def create_item(new_item: Item, item_repo: ItemRepo) -> Item:
        try:
            created_item = await item_repo.add_item(item_data=new_item)
            await item_repo.commit()
            return created_item
        except Exception as e:
            await item_repo.rollback()
            logger.error(f"Error of creating item: {e}")
            raise


    @staticmethod
    async def fetch_item_by_id(item_id: int, item_repo: ItemRepo) -> Item | None:
        try:
            response = await item_repo.get_item_by_id(item_id=item_id)
            if not response:
                raise ItemNotFound(f"Item with item_id={item_id} not found")
            else:
                return response
        except Exception as e:
            logger.error(f"Error of getting item by id: {e}")
            raise


    @staticmethod
    async def fetch_all_items(offset: int, limit: int, item_repo: ItemRepo) -> List[Item] | None:
        try:
            response = await item_repo.get_items(offset, limit)
            return response
        except Exception as e:
            logger.error(f"Error of getting all items: {e}")


    @staticmethod
    async def update_item_data(update_item: Item, item_repo: ItemRepo) -> Item | None:
        try:
            response = await item_repo.update_item(updated_item_data=update_item)
            if not response:
                await item_repo.rollback()
                raise ItemNotFound(f"No such item with item_id={update_item.id}")
            else:
                await item_repo.commit()
                return response
        except Exception as e:
            await item_repo.rollback()
            logger.error(f"Error of updating item: {e}")


    @staticmethod
    async def delete_item(item_id: int, item_repo: ItemRepo) -> bool | None:
        try:
            response = await item_repo.delete_item_by_id(item_id=item_id)
            if not response:
                await item_repo.rollback()
                raise ItemNotFound(f"No such item with item_id={item_id}")
            else:
                await item_repo.commit()
                return True
        except Exception as e:
            await item_repo.rollback()
            logger.error(f"Error of deleting item: {e}")