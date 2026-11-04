from sqlalchemy import func, select
from shop_api.schemas.cart import CartDB, CartListQuery
from shop_api.services.cart import CartService
from shop_api.models.cart import Cart
from shop_api.models.item import Item
from sqlalchemy.ext.asyncio import AsyncSession


async def test_create_cart(session: AsyncSession):
    cart_service = CartService(session)
    cart = await cart_service.create_cart()
    assert isinstance(cart, Cart)
    assert cart.id is not None
    carts_count = (await session.execute(select(func.count()).select_from(Cart))).scalar()
    assert carts_count == 1


async def test_get_cart_by_id(session: AsyncSession, cart: Cart):
    cart_service = CartService(session)
    result = await cart_service.get_cart_by_id(cart.id)
    assert isinstance(result, CartDB)
    assert cart.id == result.id
    assert cart.items == []


async def test_get_carts(session: AsyncSession, cart: Cart):
    cart_service = CartService(session)
    carts = await cart_service.get_carts(CartListQuery())
    assert len(carts) == 1
    first_cart = carts[0]
    assert isinstance(first_cart, CartDB)
    assert cart.id == first_cart.id
    assert cart.items == []

async def test_add_item_to_cart(session: AsyncSession, cart: Cart, item: Item):
    cart_service = CartService(session)
    cart_with_item = await cart_service.add_item_to_cart(cart.id, item.id)
