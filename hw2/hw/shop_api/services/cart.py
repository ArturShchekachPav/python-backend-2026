from shop_api.schemas.cart import CartListQuery
from shop_api.services.item import ItemService
from shop_api.models.cart import Cart
from shop_api.services.crud import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class CartService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud = CRUDBase(Cart, session)
        self.item_service = ItemService(session)

    async def create_cart(self) -> Cart:
        return await self.crud.create()

    async def get_carts(self, query: CartListQuery):
        db_objs = await self.session.execute(
            select(self.model).where(query).order_by(self.model.id)
        )
        return list(db_objs.scalars().all())

    async def get_cart_by_id(self) -> Cart:
        cart = await self.crud.get_by_id()
        if cart is None:
            raise Exception()
        return cart

    async def add_item_to_cart(self, cart_id, item_id) -> Cart:
        cart = self.get_cart_by_id(cart_id)
        item = self.item_service.get_item_by_id(item_id)
        cart.item.append(item.id)
        cart.price += item.price 