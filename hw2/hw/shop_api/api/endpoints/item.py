from typing import Annotated

from fastapi import APIRouter, Query

from shop_api.core.deps import SessionDep
from shop_api.schemas.item import ItemDB, ItemCreate, ItemListQuery, ItemUpdate, ItemReplace
from shop_api.services.exceptions import ItemNotFoundError
from shop_api.services.item import ItemService
from shop_api.api.exceptions import HTTPItemNotFoundError

router = APIRouter(prefix="/item", tags=["item"])

@router.post(
    "/",
    response_model=ItemDB,
)
async def create_new_item(obj_in: ItemCreate, session: SessionDep):
    item_service = ItemService(session)
    return await item_service.create_item(obj_in)

@router.get("/", response_model=list[ItemDB])
async def get_items(
    session: SessionDep,
    query: Annotated[ItemListQuery, Query()]
):
    item_service = ItemService(session)
    return await item_service.get_items(query)

@router.get(
    "/{item_id}",
    response_model=ItemDB,
)
async def get_item_by_id(item_id: int, session: SessionDep):
    item_service = ItemService(session)
    try:
        return await item_service.get_item_by_id(item_id, session)
    except ItemNotFoundError:
        raise HTTPItemNotFoundError()

@router.put(
    "/{item_id}",
    response_model=ItemDB,
)
async def replace_item_by_id(obj_in: ItemReplace, item_id: int, session: SessionDep):
    item_service = ItemService(session)
    try:
        return await item_service.update_item_by_id(obj_in, item_id)
    except ItemNotFoundError:
        raise HTTPItemNotFoundError()

@router.patch(
    "/{item_id}",
    response_model=ItemDB,
)
async def update_item_by_id(obj_in: ItemUpdate, item_id: int, session: SessionDep):
    item_service = ItemService(session)
    try:
        return await item_service.update_item_by_id(obj_in, item_id)
    except ItemNotFoundError:
        raise HTTPItemNotFoundError()

@router.delete(
    "/{item_id}",
    response_model=ItemDB,
)
async def delete_item_by_id(item_id: int, session: SessionDep):
    item_service = ItemService(session)
    try:
        return await item_service.delete_item_by_id(item_id)
    except ItemNotFoundError:
        raise HTTPItemNotFoundError()
