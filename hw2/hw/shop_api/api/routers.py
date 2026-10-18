from fastapi import APIRouter

from shop_api.api.endpoints import cart, item

main_router = APIRouter()
main_router.include_router(cart.router)
main_router.include_router(item.router)
