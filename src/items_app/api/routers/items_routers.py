import logging
from uuid import UUID
from typing import Annotated, List, Optional, Union, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from items_app.api.providers import get_items_app_service, get_companies_app_service
from items_app.api.schemas.item_schemas import ItemCreate, ItemResponse, ItemsIdList
from items_app.application.items_applications.items_applications_service import (
    ItemsApplicationsService,
)
from items_app.application.companies_applications.companies_applications_service import (
    CompaniesApplicationsService,
)
from items_app.application.items_applications.items_applications_exceptions import (
    ItemNotFound, NoAccessToItem
)
from items_app.application.companies_applications.companies_applications_exceptions import (
    CompanyNotFound,
)
from items_app.infrastructure.postgres.models import Item


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("", summary="Создание товара")
async def create_new_item(
    new_item_schema: ItemCreate,
    items_service: Annotated[ItemsApplicationsService, Depends(get_items_app_service)],
):
    try:
        new_item_data = Item(
            title=new_item_schema.title,
            price=new_item_schema.price,
            company_id=new_item_schema.company_id,
        )
        new_item = await items_service.create_item(new_item_data)
        item_response = ItemResponse.model_validate(new_item)
        return {"message": "New item created successfully", "item": item_response}
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create item")


@router.get(
    "/get-many",
    summary="Вывод нескольких товаров компании по ID (GET) для небольших списков",
    response_model=List[ItemResponse],
)
async def get_items_by_ids_get(
    company_id: UUID,
    items_service: Annotated[ItemsApplicationsService, Depends(get_items_app_service)],
    item_ids: Optional[List[UUID]] = Query(
        default=None, description="Список UUID товаров"
    ),
):
    if not item_ids:
        raise HTTPException(status_code=422, detail="Empty list of item IDs provided")

    try:
        items = await items_service.fetch_items_by_ids(item_ids, company_id)
        if not items:
            raise ItemNotFound("No items found for the provided IDs")
        item_response = [ItemResponse.model_validate(item) for item in items]
        return item_response
    except ItemNotFound as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch items")


@router.get("/{item_id}", summary="Вывод товара по ID", response_model=ItemResponse)
async def get_item_by_id(
    item_id: UUID,
    company_id: UUID,
    items_service: Annotated[ItemsApplicationsService, Depends(get_items_app_service)],
):
    try:
        item = await items_service.fetch_item_by_id(item_id, company_id)
        item_response = ItemResponse.model_validate(item)
        return item_response
    except NoAccessToItem as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ItemNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch item")


@router.post(
    "/get-many",
    summary="Вывод нескольких товаров компании по ID (POST) для больших списков",
    response_model=List[ItemResponse],
)
async def get_items_by_ids_post(
    item_ids: ItemsIdList,
    company_id: UUID,
    items_service: Annotated[ItemsApplicationsService, Depends(get_items_app_service)],
):
    if not item_ids.item_ids:
        raise HTTPException(status_code=422, detail="Empty list of item IDs provided")

    try:
        items = await items_service.fetch_items_by_ids(item_ids.item_ids, company_id)
        if not items:
            raise ItemNotFound("No items found for the provided IDs")
        item_response = [ItemResponse.model_validate(item) for item in items]
        return item_response
    except ItemNotFound as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch items")


@router.get(
    "/company/{company_id}",
    summary="Вывод всех товаров компании по ID компании",
    response_model=List[ItemResponse],
)
async def get_items_of_company_by_company_id(
    company_id: UUID,
    items_service: Annotated[ItemsApplicationsService, Depends(get_items_app_service)],
    companies_service: Annotated[
        CompaniesApplicationsService, Depends(get_companies_app_service)
    ],
):
    try:
        current_company = await companies_service.fetch_company_by_id(company_id)
        if not current_company:
            raise CompanyNotFound(f"Company with company_id={company_id} not found")
        items = await items_service.fetch_items_of_company_by_company_id(company_id)
        if not items:
            raise ItemNotFound(
                f"No items found for company with company_id={company_id}"
            )
        item_response = [ItemResponse.model_validate(item) for item in items]
        return item_response
    except CompanyNotFound as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ItemNotFound as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch items of company")


@router.get(
    "", summary="Вывод всех товаров", response_model=Union[List[ItemResponse], Dict]
)
async def get_all_items(
    items_service: Annotated[ItemsApplicationsService, Depends(get_items_app_service)],
    offset: Optional[int] = 0,
    limit: Optional[int] = 10,
):
    try:
        items = await items_service.fetch_all_items(offset, limit)
        if items:
            item_response = [ItemResponse.model_validate(item) for item in items]
            return item_response
        else:
            return {"message": "No items in database"}
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch items")


@router.put("/{item_id}", summary="Изменение товара по ID")
async def update_item_data_by_id(
    item_id: UUID,
    update_data: ItemCreate,
    items_service: Annotated[ItemsApplicationsService, Depends(get_items_app_service)],
):
    try:
        update_item_data = Item(
            id=item_id,
            title=update_data.title,
            price=update_data.price,
            company_id=update_data.company_id,
        )
        updated_item = await items_service.update_item_data(update_item_data)
        item_response = ItemResponse.model_validate(updated_item)
        return {"message": "Item updated successfully", "item": item_response}
    except ItemNotFound as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update item")


@router.delete("/delete-many", summary="Удаление нескольких товаров по ID")
async def delete_items_by_ids(
    item_ids: ItemsIdList,
    company_id: UUID,
    items_service: Annotated[ItemsApplicationsService, Depends(get_items_app_service)],
):
    try:
        if not item_ids.item_ids:
            raise HTTPException(
                status_code=422, detail="Empty list of item IDs provided"
            )
        item_ids_list = [item_id for item_id in item_ids.item_ids]
        await items_service.delete_items(item_ids_list, company_id)
        item_ids_str = ", ".join(str(item_id) for item_id in item_ids_list)
        return {"message": f"Items with IDs [{item_ids_str}] have been deleted"}
    except ItemNotFound as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete items")


@router.delete("/{item_id}", summary="Удаление товара по ID")
async def delete_item_by_id(
    item_id: UUID,
    company_id: UUID,
    items_service: Annotated[ItemsApplicationsService, Depends(get_items_app_service)],
):
    try:
        await items_service.delete_item(item_id, company_id)
        return {"message": f"Item with item_id={item_id} was deleted"}
    except ItemNotFound as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete item")
