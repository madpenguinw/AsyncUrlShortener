from datetime import datetime
from typing import Any, Generic, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from db.db import Base

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUD:

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def get_multi(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError


class UrlCRUD(
    CRUD, Generic[ModelType, CreateSchemaType, UpdateSchemaType]
):

    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get(
        self, db: AsyncSession, value: Any,
        check: bool = False, short_url: bool = False
    ) -> ModelType | None:
        """Get the object"""

        if check:
            statement = select(self._model).where(
                self._model.full_url == value and self._model.is_active)
        elif short_url:
            statement = select(self._model).where(
                self._model.short_url == value and self._model.is_active)
        else:
            statement = select(self._model).where(
                self._model.id == value and self._model.is_active)
        results = await db.execute(statement=statement)

        return results.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        *,
        field: str = None,
        value: str = None,
        obj_in: CreateSchemaType
    ) -> ModelType:
        """Create the object"""

        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)

        if field and value:
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    async def update(
        self,
        id: int,
        field: str,
        db: AsyncSession
    ) -> ModelType:
        """Update the Url object."""

        statement = select(self._model).where(
            self._model.id == id and self._model.is_active)
        results = await db.execute(statement=statement)
        url_obj = results.scalar_one_or_none()

        value: bool | str = False

        if field == 'clicks':
            # case then it is needed to increment 'click' value
            # another case is situation with fake 'deletion' of Url object
            value: bool | str = url_obj.clicks + 1

        setattr(url_obj, field, value)

        db.add(url_obj)
        await db.commit()
        await db.refresh(url_obj)

        return url_obj


class ClickCRUD(
    CRUD, Generic[ModelType, CreateSchemaType]
):

    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get_multi(
        self, url_id: int, db: AsyncSession, skip=0, limit=100
    ) -> list[ModelType]:
        """Get all (or as many as it nedeed) Click objects"""

        statement = select(self._model).where(
            self._model.url_id == url_id).offset(skip).limit(limit)
        results = await db.execute(statement=statement)

        return results.scalars().all()

    async def create(
        self,
        url_id: int,
        client: str,
        db: AsyncSession
    ) -> None:
        """Create the Click object"""

        click_obj: Type[ModelType] = self._model(
            url_id=url_id,
            date=datetime.now(),
            client=client
        )

        db.add(click_obj)
        await db.commit()
        await db.refresh(click_obj)
        return
