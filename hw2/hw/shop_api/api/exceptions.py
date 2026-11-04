from fastapi import HTTPException, status

from shop_api.core.constants import CART_NOT_FOUND_MESSAGE, ITEM_NOT_FOUND_MESSAGE


class HTTPItemNotFoundError(HTTPException):
    '''HTTPException for Item Not Found error.'''

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ITEM_NOT_FOUND_MESSAGE
        )


class HTTPCartNotFoundError(HTTPException):
    '''HTTPException for Cart Not Found error.'''

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CART_NOT_FOUND_MESSAGE
        )
