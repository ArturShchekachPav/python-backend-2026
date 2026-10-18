from fastapi import APIRouter, Query, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from shop_api.core.db import get_async_session
from shop_api.schemas.cart import CartListQuery
from shop_api.services.cart import CartService

router = APIRouter(prefix="/cart", tags=["cart"])

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]

@router.post(
    "/",
    response_model=CartDB,
)
async def create_new_cart(session: SessionDep):
    cart_service = CartService(session)
    return await cart_service.create_cart()


@router.get("/", response_model=list[CartDB])
async def get_carts(
    session: SessionDep,
    query: Annotated[CartListQuery, Query()]
):
    cart_service = CartService(session)
    return await cart_service.get_carts(query)

@router.get(
    "/{cart_id}",
    response_model=CartDB,
)
async def get_cart_by_id(cart_id: int, session: SessionDep):
    cart_service = CartService(session)
    try:
        return await cart_service.get_cart_by_id(cart_id)
    except CartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found"
        )

@router.post(
    "/{cart_id}/add/{item_id}",
    response_model=CartDB,
)
async def add_item_cart(cart_id: int, item_id: int, session: SessionDep):
    cart_service = CartService(session)
    try:
            return await cart_service.add_item_to_cart(cart_id, item_id)
    except CartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found"
        )
    except ItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )