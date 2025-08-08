import logging
from typing import Annotated, List, Optional, Union, Dict
from fastapi import APIRouter, Depends, HTTPException
from items_app.api.providers import get_item_repo
from items_app.api.schemas import ItemCreate, ItemResponse
from items_app.application.application import ItemApplications
from items_app.application.application_exceptions import ItemNotFound
from items_app.infrastructure.models import Item
from items_app.infrastructure.repository import ItemRepo


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("", summary="Создание товара")
async def create_new_item(
        new_item_schema: ItemCreate,
        item_repo: Annotated[ItemRepo, Depends(get_item_repo)]
):
    try:
        new_item_data = Item(title=new_item_schema.title, price=new_item_schema.price)
        new_item = await ItemApplications.create_item(new_item_data, item_repo)
        item_response = ItemResponse.model_validate(new_item)
        return {"message": "New item created successfully", "item": item_response}
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create item")


@router.get("/{item_id}", summary="Вывод товара по ID", response_model=ItemResponse)
async def get_item_by_id(
        item_id: int,
        item_repo: Annotated[ItemRepo, Depends(get_item_repo)]
):
    try:
        item = await ItemApplications.fetch_item_by_id(item_id, item_repo)
        item_response = ItemResponse.model_validate(item)
        return item_response
    except ItemNotFound as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch item")


@router.get("", summary="Вывод всех заметок", response_model=Union[List[ItemResponse], Dict])
async def get_all_items(
        item_repo: Annotated[ItemRepo, Depends(get_item_repo)],
        offset: Optional[int] = 0,
        limit: Optional[int] = 10
):
    try:
        items = await ItemApplications.fetch_all_items(offset, limit, item_repo)
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
        item_id: int,
        update_data: ItemCreate,
        item_repo: Annotated[ItemRepo, Depends(get_item_repo)]
):
    try:
        update_item_data = Item(id=item_id, title=update_data.title, price=update_data.price)
        updated_item = await ItemApplications.update_item_data(update_item_data, item_repo)
        item_response = ItemResponse.model_validate(updated_item)
        return {"message": "Item updated successfully", "item": item_response}
    except ItemNotFound as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update item")


@router.delete("/{item_id}", summary="Удаление товара по ID")
async def delete_note_by_id(
        item_id: int,
        item_repo: Annotated[ItemRepo, Depends(get_item_repo)]
):
    try:
        await ItemApplications.delete_item(item_id, item_repo)
        return {"message": f"Item with item_id={item_id} was deleted"}
    except ItemNotFound as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update item")