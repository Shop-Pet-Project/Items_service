import logging
from uuid import UUID
from typing import List, Optional
from items_app.application.application_exceptions import ItemNotFound, CompanyNotFound
from items_app.infrastructure.postgres.models import Item, Company
from items_app.infrastructure.postgres.repository import ItemRepo, CompanyRepo


logger = logging.getLogger(__name__)


class ItemApplications:
    @staticmethod
    async def create_item(new_item: Item, item_repo: ItemRepo) -> Optional[Item]:
        try:
            created_item = await item_repo.add_item(item_data=new_item)
            await item_repo.commit()
            return created_item
        except Exception as e:
            await item_repo.rollback()
            logger.error(f"Error of creating item: {e}")
            raise

    @staticmethod
    async def fetch_item_by_id(item_id: UUID, item_repo: ItemRepo) -> Item | None:
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
    async def get_missing_ids(
        existing_items: Optional[List[Item]], item_ids: List[UUID]
    ) -> List[str]:
        """Метод для получения списка отсутствующих ID товаров из запрошенного списка."""
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

    @staticmethod
    async def fetch_items_by_ids(
        item_ids: List[UUID], item_repo: ItemRepo
    ) -> List[Item] | None:
        try:
            response = await item_repo.get_items_by_ids(item_ids=item_ids)
            if not response or len(response) != len(item_ids):
                missing_ids = await ItemApplications.get_missing_ids(response, item_ids)
                raise ItemNotFound(f"No items found with IDs {', '.join(missing_ids)}")
            else:
                return response
        except Exception as e:
            logger.error(f"Error of getting items by ids: {e}")
            raise

    @staticmethod
    async def fetch_items_of_company_by_company_id(
        company_id: UUID, item_repo: ItemRepo
    ) -> List[Item] | None:
        try:
            response = await item_repo.get_items_by_company_id(company_id=company_id)
            if not response:
                raise ItemNotFound(
                    f"No items found for company with company_id={company_id}"
                )
            else:
                return response
        except Exception as e:
            logger.error(f"Error of getting items by company id: {e}")
            raise

    @staticmethod
    async def fetch_all_items(
        offset: Optional[int], limit: Optional[int], item_repo: ItemRepo
    ) -> List[Item] | None:
        try:
            response = await item_repo.get_items(offset, limit)
            return response
        except Exception as e:
            logger.error(f"Error of getting all items: {e}")
            raise

    @staticmethod
    async def update_item_data(update_item: Item, item_repo: ItemRepo) -> Item | None:
        try:
            response = await item_repo.update_item(updated_item_data=update_item)
            if not response:
                raise ItemNotFound(f"No such item with item_id={update_item.id}")
            else:
                await item_repo.commit()
                return response
        except Exception as e:
            await item_repo.rollback()
            logger.error(f"Error of updating item: {e}")
            raise

    @staticmethod
    async def delete_item(item_id: UUID, item_repo: ItemRepo) -> bool | None:
        try:
            response = await item_repo.delete_item_by_id(item_id=item_id)
            if not response:
                raise ItemNotFound(f"No such item with item_id={item_id}")
            else:
                await item_repo.commit()
                return True
        except Exception as e:
            await item_repo.rollback()
            logger.error(f"Error of deleting item: {e}")
            raise

    @staticmethod
    async def delete_items(item_ids: List[UUID], item_repo: ItemRepo) -> bool | None:
        try:
            existing_items = await item_repo.get_items_by_ids(item_ids=item_ids)
            if not existing_items or len(existing_items) != len(item_ids):
                missing_ids = await ItemApplications.get_missing_ids(
                    existing_items, item_ids
                )
                raise ItemNotFound(f"No items found with IDs {', '.join(missing_ids)}")

            await item_repo.delete_items_by_ids(item_ids=item_ids)
            await item_repo.commit()
            return True
        except Exception as e:
            await item_repo.rollback()
            logger.error(f"Error of deleting items: {e}")
            raise


class CompanyApplications:
    @staticmethod
    async def create_company(
        new_company: Company, company_repo: CompanyRepo
    ) -> Optional[Company]:
        try:
            created_company = await company_repo.add_company(company_data=new_company)
            await company_repo.commit()
            return created_company
        except Exception as e:
            await company_repo.rollback()
            logger.error(f"Error of creating company: {e}")
            raise

    @staticmethod
    async def fetch_company_by_id(
        company_id: UUID, company_repo: CompanyRepo
    ) -> Company | None:
        try:
            response = await company_repo.get_company_by_id(company_id=company_id)
            if not response:
                raise CompanyNotFound(f"Company with company_id={company_id} not found")
            else:
                return response
        except Exception as e:
            logger.error(f"Error of getting company by id: {e}")
            raise

    @staticmethod
    async def fetch_all_companies(
        offset: Optional[int], limit: Optional[int], company_repo: CompanyRepo
    ) -> List[Company] | None:
        try:
            response = await company_repo.get_all_companies(offset, limit)
            return response
        except Exception as e:
            logger.error(f"Error of getting all companies: {e}")
            raise

    @staticmethod
    async def update_company_data(
        update_company: Company, company_repo: CompanyRepo
    ) -> Company | None:
        try:
            response = await company_repo.update_company_data(
                updated_company_data=update_company
            )
            if not response:
                raise CompanyNotFound(
                    f"No such company with company_id={update_company.id}"
                )
            else:
                await company_repo.commit()
                return response
        except Exception as e:
            await company_repo.rollback()
            logger.error(f"Error of updating company: {e}")
            raise

    @staticmethod
    async def delete_company(
        company_id: UUID, company_repo: CompanyRepo
    ) -> bool | None:
        try:
            response = await company_repo.remove_company_by_id(company_id=company_id)
            if not response:
                raise CompanyNotFound(f"No such company with company_id={company_id}")
            else:
                await company_repo.commit()
                return True
        except Exception as e:
            await company_repo.rollback()
            logger.error(f"Error of deleting company: {e}")
            raise
