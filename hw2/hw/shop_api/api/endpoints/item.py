from fastapi import APIRouter

from shop_api.services.item import ItemService

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

@router.put(
    "/{item_id}",
    response_model=ItemDB,
)
async def full_update_item_by_id(obj_in: ItemFullUpdate, item_id: int, session: SessionDep):
    item_service = ItemService(session)
    try:
        return await item_service.update_item_by_id(obj_in, item_id)
    except ItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

@router.patch(
    "/{item_id}",
    response_model=ItemDB,
)
async def partially_update_item_by_id(obj_in: ItemPartiallyUpdate, item_id: int, session: SessionDep):
    item_service = ItemService(session)
    try:
        return await item_service.update_item_by_id(obj_in, item_id)
    except ItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

@router.delete(
    "/{item_id}",
    response_model=ItemDB,
)
async def delete_item_by_id(item_id: int, session: SessionDep):
    item_service = ItemService(session)
    try:
        return await item_service.delete_item_by_id(item_id)
    except ItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )