from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BrandRequest(BaseModel):
    model_config = ConfigDict(validate_by_name=False, validate_by_alias=True)

    name: str
    aliases: set[str] = Field(default_factory=set)


class BrandResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, validate_by_name=True, validate_by_alias=False, serialize_by_alias=True
    )

    id: UUID
    name: str
    aliases: set[str]
