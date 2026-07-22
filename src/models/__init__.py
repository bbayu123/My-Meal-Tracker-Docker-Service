"""
Contains all object-relational mappings for this application.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from .brand import Brand
from .brand_alias import BrandAlias
