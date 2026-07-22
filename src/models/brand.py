import typing
from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if typing.TYPE_CHECKING:
    from .brand_alias import BrandAlias


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(unique=True)

    aliases: Mapped[set[BrandAlias]] = relationship(back_populates="brand", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Brand(id={self.id!r}, name={self.name!r}, aliases={self.aliases!r})"
