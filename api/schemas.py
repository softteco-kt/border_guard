import datetime
from typing import Any
from uuid import UUID

import peewee
from pydantic import BaseModel
from pydantic.utils import GetterDict


class PeeweeGetterDict(GetterDict):
    """When you access a relationship in a Peewee object, like in some_user.items, Peewee doesn't provide a list of Item."""

    def get(self, key: Any, default: Any = None):
        res = getattr(self._obj, key, default)
        if isinstance(res, peewee.ModelSelect):
            return list(res)
        return res


class CarsMetaData(BaseModel):
    amount: int


class BorderCaptureOut(BaseModel):
    id: UUID
    created_at: datetime.datetime
    image_path: str
    number_of_cars: int | None = None
    processed: bool | None = None
    processed_at: datetime.datetime | None = None
    is_valid: bool | None = None

    class Config:
        orm_mode = True
