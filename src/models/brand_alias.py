import typing
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if typing.TYPE_CHECKING:
    from .brand import Brand


class BrandAlias(Base):
    __tablename__ = "brand_aliases"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    alias: Mapped[str] = mapped_column(unique=True)
    brand_id: Mapped[UUID] = mapped_column(ForeignKey("brands.id"))

    brand: Mapped[Brand] = relationship(back_populates="aliases")

    def __repr__(self) -> str:
        return f"BrandAlias(id={self.id!r}, alias={self.alias!r})"
