from sqlalchemy import Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shop_api.core.db import Base, CommonMixin


class Cart(CommonMixin, Base):
    items: Mapped[list["Item"]] = relationship(
        back_populates="cart",
        cascade="all, delete-orphan",
    )
    price: Mapped[float] = mapped_column(
        Float, nullable=False, default=0
    )
