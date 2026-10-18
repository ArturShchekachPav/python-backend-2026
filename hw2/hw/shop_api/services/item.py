from shop_api.models.item import Item
from shop_api.services.crud import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class ItemService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud = CRUDBase(Item, session)

    async def create_item(self, obj_in: ItemCreate) -> Item:
        return await self.create_item(obj_in)

    async def get_items(self, query: ItemListQuery) -> list[Item]:
        db_objs = await self.session.execute(
            select(self.model).where(query).order_by(self.model.id)
        )
        return list(db_objs.scalars().all())

    async def get_item_by_id(self, item_id: int) -> Item:
        item = await self.crud.get_by_id(item_id)
        if item is None:
            raise Exception()
        return item

    async def update_item_by_id(self, obj_in: ItemCreate | ItemUpdate, item_id: int):
        item = await self.get_item_by_id(item_id)
        return await self.crud.update(item, obj_in)

    async def delete_item_by_id(self, item_id: int) -> None:
        item = await self.get_item_by_id(item_id)
        return await self.crud.remove(item)
        