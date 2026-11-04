from fastapi.testclient import TestClient
from fastapi import status
import pytest
from sqlalchemy import func, select
from shop_api.core.constants import ITEM_NOT_FOUND_MESSAGE, ITEM_PREFIX_URL, ITEM_DETAILS_URL
from shop_api.schemas.item import ItemDB, ItemListQuery, ItemCreate, ItemReplace, ItemUpdate
from shop_api.services.item import ItemService
from shop_api.models.item import Item
from sqlalchemy.ext.asyncio import AsyncSession

from shop_api.services.exceptions import ItemNotFoundError

CREATE_ITEM_DATA = {
    'name': 'Item',
    'price': 10
}

UPDATE_ITEM_DATA = {
    'name': 'New Item',
    'price': 20
}

async def test_create_item(session: AsyncSession):
    item_service = ItemService(session)
    item = await item_service.create_item(ItemCreate.model_validate(CREATE_ITEM_DATA))
    assert isinstance(item, Item)
    assert isinstance(item.id, int)
    assert item.name == CREATE_ITEM_DATA['name']
    assert item.price == CREATE_ITEM_DATA['price']
    assert item.deleted == False
    items_count = (await session.execute(select(func.count()).select_from(Item))).scalar()
    assert items_count == 1

async def test_get_item_by_id(session: AsyncSession, item: Item):
    item_service = ItemService(session)
    founded_item = await item_service.get_item_by_id(item.id)
    assert isinstance(founded_item, Item)
    assert founded_item.id == item.id
    assert founded_item.price == item.price
    assert founded_item.name == item.name
    assert founded_item.deleted == item.deleted


async def test_get_item_by_id_not_exist(session: AsyncSession):
    item_service = ItemService(session)
    with pytest.raises(ItemNotFoundError):
        await item_service.get_item_by_id(99999)

async def test_get_active_item_by_id(session: AsyncSession, item: Item):
    item_service = ItemService(session)
    founded_item = await item_service.get_active_item_by_id(item.id)
    assert isinstance(founded_item, Item)
    assert founded_item.id == item.id
    assert founded_item.price == item.price
    assert founded_item.name == item.name
    assert founded_item.deleted == item.deleted

async def test_get_active_item_by_id(session: AsyncSession, deleted_item: Item):
    item_service = ItemService(session)
    with pytest.raises(ItemNotFoundError):
        await item_service.get_active_item_by_id(deleted_item.id)


async def test_get_carts(session: AsyncSession, item: Item):
    item_service = ItemService(session)
    items = await item_service.get_items(ItemListQuery())
    assert len(items) == 1
    first_item = items[0]
    assert isinstance(first_item, Item)
    assert item.id == first_item.id
    assert first_item.price == item.price
    assert first_item.name == item.name
    assert first_item.deleted == item.deleted


async def test_update_item_by_id(session: AsyncSession, item: Item):
    item_service = ItemService(session)
    updated_item = await item_service.update_item_by_id(ItemReplace.model_validate(UPDATE_ITEM_DATA), item.id)
    assert isinstance(updated_item, Item)
    assert updated_item.id == item.id
    assert updated_item.price == UPDATE_ITEM_DATA['price']
    assert updated_item.name == UPDATE_ITEM_DATA['name']
    assert updated_item.deleted == item.deleted


async def test_delete_item_by_id(session: AsyncSession, item: Item):
    item_service = ItemService(session)
    deleted_item = await item_service.delete_item_by_id(item.id)
    assert isinstance(deleted_item, Item)
    assert deleted_item.id == item.id
    assert deleted_item.price == item.price
    assert deleted_item.name == item.name
    assert deleted_item.deleted == True


def test_create_item_endpoint(test_client: TestClient):
    response = test_client.post(ITEM_PREFIX_URL, json=CREATE_ITEM_DATA)
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    item = ItemDB.model_validate(body)
    assert item.name == CREATE_ITEM_DATA['name']
    assert item.price == CREATE_ITEM_DATA['price']
    assert item.deleted == False


def test_get_item_by_id_endpoint(test_client: TestClient, item: Item):
    request_url = ITEM_PREFIX_URL + ITEM_DETAILS_URL.format(item_id=item.id)
    response = test_client.get(request_url)
    body = response.json()
    founded_item = ItemDB.model_validate(body)
    assert founded_item.id == item.id
    assert founded_item.name == item.name
    assert founded_item.price == item.price
    assert founded_item.deleted == item.deleted


def test_get_item_by_id_not_exist_endpoint(test_client: TestClient):
    request_url = ITEM_PREFIX_URL + ITEM_DETAILS_URL.format(item_id=9999)
    response = test_client.get(request_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body['detail'] == ITEM_NOT_FOUND_MESSAGE

def test_get_item_by_id_deleted_endpoint(test_client: TestClient, deleted_item: Item):
    request_url = ITEM_PREFIX_URL + ITEM_DETAILS_URL.format(item_id=deleted_item.id)
    response = test_client.get(request_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body['detail'] == ITEM_NOT_FOUND_MESSAGE


def test_get_items_endpoint(test_client: TestClient, item: Item):
    response = test_client.get(ITEM_PREFIX_URL)
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    first_item = ItemDB.model_validate(body[0])
    assert item.id == first_item.id
    assert item.price == first_item.price
    assert item.name == first_item.name
    assert item.deleted == first_item.deleted


def test_replace_item_by_id_endpoint(test_client: TestClient, item: Item):
    request_url = ITEM_PREFIX_URL + ITEM_DETAILS_URL.format(item_id=item.id)
    response = test_client.put(request_url, json=UPDATE_ITEM_DATA)
    body = response.json()
    replaced_item = ItemDB.model_validate(body)
    assert replaced_item.id == item.id
    assert replaced_item.name == UPDATE_ITEM_DATA['name']
    assert replaced_item.price == UPDATE_ITEM_DATA['price']
    assert replaced_item.deleted == item.deleted


def test_update_item_by_id_endpoint(test_client: TestClient, item: Item):
    request_url = ITEM_PREFIX_URL + ITEM_DETAILS_URL.format(item_id=item.id)
    response = test_client.patch(request_url, json={ 'name': UPDATE_ITEM_DATA['name'] })
    body = response.json()
    updated_item = ItemDB.model_validate(body)
    assert updated_item.id == item.id
    assert updated_item.name == UPDATE_ITEM_DATA['name']
    assert updated_item.price == item.price
    assert updated_item.deleted == item.deleted


def test_delete_item_by_id_endpoint(test_client: TestClient, item: Item):
    request_url = ITEM_PREFIX_URL + ITEM_DETAILS_URL.format(item_id=item.id)
    response = test_client.delete(request_url)
    body = response.json()
    deleted_item = ItemDB.model_validate(body)
    assert deleted_item.id == item.id
    assert deleted_item.name == item.name
    assert deleted_item.price == item.price
    assert deleted_item.deleted == True
