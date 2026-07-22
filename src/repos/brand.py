from typing import overload
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Brand, BrandAlias
from ..schemas import BrandRequest, BrandResponse


class BrandRepo:
    db: Session

    def __init__(self, db: Session) -> None:
        assert db is not None
        self.db = db

    def get_all(self) -> list[Brand]:
        brands = self.db.execute(select(Brand)).scalars()
        return list(brands)

    def get_one(self, id: UUID) -> Brand | None:
        brand = self.db.execute(select(Brand).where(Brand.id == id)).scalar_one_or_none()
        return brand

    def find_by_name_or_alias(self, name: str) -> Brand | None:
        brand = self.db.execute(select(Brand).where(Brand.name == name)).scalar_one_or_none()

        if brand is not None:
            return brand

        alias = self.db.execute(select(BrandAlias).where(BrandAlias.alias == name)).scalar_one_or_none()
        if alias is not None:
            return alias.brand

        return None

    def create(self, data: BrandRequest) -> Brand:
        _brand = self.find_by_name_or_alias(data.name)
        if _brand is not None:
            if _brand.name == data.name:
                raise ValueError(f"'{data.name}' already exists")
            else:
                raise ValueError(f"'{data.name}' already exists as an alias of '{_brand.name}'")
        del _brand

        brand = Brand(name=data.name, aliases={BrandAlias(alias=alias) for alias in data.aliases})
        self.db.add(brand)
        self.db.commit()

        self.db.refresh(brand)
        return brand

    def delete(self, id: UUID) -> None:
        brand = self.get_one(id)
        if brand is None:
            raise ValueError(f"'{id}' not found in Brand")

        self.db.delete(brand)
        self.db.commit()

    def add_alias(self, id: UUID, alias: str) -> Brand | None:
        brand = self.get_one(id)
        if brand is None:
            return None

        _brand = self.find_by_name_or_alias(alias)
        if _brand is not None:
            if _brand.name == alias:
                raise ValueError(f"'{alias}' already exists as a Brand")
            else:
                raise ValueError(f"'{alias}' already exists as an alias of '{_brand.name}'")
        del _brand

        brand.aliases.add(BrandAlias(alias=alias))
        self.db.commit()
        return brand

    def remove_alias(self, id: UUID, alias: str) -> Brand | None:
        brand = self.get_one(id)
        if brand is None:
            return None

        brand_alias = next((a for a in brand.aliases if a.alias == alias), None)
        if brand_alias is None:
            raise ValueError(f"'{alias}' is not part of Brand")

        self.db.delete(brand_alias)
        self.db.commit()
        return brand

    def merge(self, *, id_remove: UUID, id_keep: UUID) -> Brand:
        brand_remove = self.get_one(id_remove)
        brand_keep = self.get_one(id_keep)
        if brand_remove is None:
            raise ValueError(f"'{id_remove}' not found in 'Brand'")
        if brand_keep is None:
            raise ValueError(f"'{id_keep}' not found in 'Brand'")

        # Create new brand alias from brand_from and assign to brand_to, and also merge aliases
        brand_alias = BrandAlias(alias=brand_remove.name)
        brand_keep.aliases.add(brand_alias)
        while len(brand_remove.aliases) > 0:
            brand_keep.aliases.add(brand_remove.aliases.pop())
        self.db.flush()

        # Reassign the brand of relevant foods to brand_to
        # TODO Food not implemented
        self.db.flush()

        # Delete the old brand from the database
        self.db.delete(brand_remove)
        self.db.commit()
        return brand_keep

    @classmethod
    @overload
    def to_response(cls, brand: Brand) -> BrandResponse: ...

    @classmethod
    @overload
    def to_response(cls, brand: list[Brand]) -> list[BrandResponse]: ...

    @classmethod
    def to_response(cls, brand: Brand | list[Brand]) -> BrandResponse | list[BrandResponse]:
        if isinstance(brand, list):
            return [cls.to_response(b) for b in brand]
        else:
            return BrandResponse(id=brand.id, name=brand.name, aliases={alias.alias for alias in brand.aliases})
