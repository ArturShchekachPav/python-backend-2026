from fastapi.testclient import TestClient
from fastapi import status
import pytest
from sqlalchemy import func, select
from shop_api.core.constants import CART_NOT_FOUND_MESSAGE, ITEM_NOT_FOUND_MESSAGE, CART_PREFIX_URL, CART_DETAILS_URL, ADD_ITEM_TO_CART_URL
from shop_api.schemas.cart import CartDB, CartItemDB, CartListQuery
from shop_api.services.cart import CartService
from shop_api.models.cart import Cart
from shop_api.models.item import Item
from sqlalchemy.ext.asyncio import AsyncSession

from shop_api.services.exceptions import CartNotFoundError, ItemNotFoundError


async def test_create_cart(session: AsyncSession):
    cart_service = CartService(session)
    cart = await cart_service.create_cart()
    assert isinstance(cart, Cart)
    assert cart.id is not None
    carts_count = (await session.execute(select(func.count()).select_from(Cart))).scalar()
    assert carts_count == 1


async def test_get_cart_by_id(session: AsyncSession, cart: Cart):
    cart_service = CartService(session)
    founded_cart = await cart_service.get_cart_by_id(cart.id)
    assert isinstance(founded_cart, CartDB)
    assert cart.id == founded_cart.id
    assert cart.items == []
    assert founded_cart.price == 0


async def test_get_cart_by_id_not_exist(session: AsyncSession):
    cart_service = CartService(session)
    with pytest.raises(CartNotFoundError):
        await cart_service.get_cart_by_id(99999)


async def test_get_carts(session: AsyncSession, cart: Cart):
    cart_service = CartService(session)
    carts = await cart_service.get_carts(CartListQuery())
    assert len(carts) == 1
    first_cart = carts[0]
    assert isinstance(first_cart, CartDB)
    assert cart.id == first_cart.id
    assert cart.items == []
    assert first_cart.price == 0


async def test_add_item_to_cart(session: AsyncSession, cart: Cart, item: Item):
    cart_service = CartService(session)
    cart_with_item = await cart_service.add_item_to_cart(cart.id, item.id)
    assert isinstance(cart_with_item, CartDB)
    assert cart.id == cart_with_item.id
    assert len(cart.items) == 1
    item_in_cart = cart_with_item.items[0]
    assert isinstance(item_in_cart, CartItemDB)
    assert item.id == item_in_cart.id
    assert item.name == item_in_cart.name
    assert item_in_cart.quantity == 1
    assert cart_with_item.price == item.price

async def test_add_item_to_cart_where_cart_not_exist(session: AsyncSession, item: Item):
    cart_service = CartService(session)
    with pytest.raises(CartNotFoundError):
        await cart_service.add_item_to_cart(9999, item.id)


async def test_add_item_to_cart_where_item_not_exist(session: AsyncSession, cart: Cart):
    cart_service = CartService(session)
    with pytest.raises(ItemNotFoundError):
        await cart_service.add_item_to_cart(cart.id, 9999)

def test_create_cart_endpoint(test_client: TestClient):
    response = test_client.post(CART_PREFIX_URL)
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert 'id' in body

def test_get_cart_by_id_endpoint(test_client: TestClient, cart: Cart):
    request_url = CART_PREFIX_URL + CART_DETAILS_URL.format(cart_id=cart.id)
    response = test_client.get(request_url)
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    cart_out = CartDB.model_validate(body)
    assert cart_out.id == cart.id
    assert cart_out.items == []
    assert cart_out.price == 0


def test_get_cart_by_id_not_exist_endpoint(test_client: TestClient):
    request_url = CART_PREFIX_URL + CART_DETAILS_URL.format(cart_id=9999)
    response = test_client.get(request_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body['detail'] == CART_NOT_FOUND_MESSAGE


def test_add_item_to_cart_endpoint(test_client: TestClient, cart: Cart, item: Item):
    request_url = CART_PREFIX_URL + ADD_ITEM_TO_CART_URL.format(cart_id=cart.id, item_id=item.id)
    response = test_client.post(request_url)
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    cart_out = CartDB.model_validate(body)
    assert cart_out.id == cart.id
    assert cart_out.price == item.price
    assert len(cart_out.items) == 1
    item_in_cart = cart_out.items[0]
    assert isinstance(item_in_cart, CartItemDB)
    assert item.id == item_in_cart.id
    assert item.name == item_in_cart.name
    assert item_in_cart.quantity == 1


def test_add_item_to_cart_where_cart_not_exist_endpoint(test_client: TestClient, item: Item):
    request_url = CART_PREFIX_URL + ADD_ITEM_TO_CART_URL.format(cart_id=9999, item_id=item.id)
    response = test_client.post(request_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body['detail'] == CART_NOT_FOUND_MESSAGE


def test_add_item_to_cart_where_item_not_exist_endpoint(test_client: TestClient, cart: Cart):
    request_url = CART_PREFIX_URL + ADD_ITEM_TO_CART_URL.format(cart_id=cart.id, item_id=9999)
    response = test_client.post(request_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body['detail'] == ITEM_NOT_FOUND_MESSAGE
