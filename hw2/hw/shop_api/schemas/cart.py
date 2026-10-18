from pydantic import BaseModel, Field
from typing import Optional

class CartListQuery(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(10, gt=0)
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    min_quantity: Optional[int] = Field(None, ge=0)
    max_quantity: Optional[int] = Field(None, ge=0)