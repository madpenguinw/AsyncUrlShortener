from typing import Any, Generic, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from db.db import Base

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class Repository:

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def get_multi(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError


class RepositoryDB(
    Repository, Generic[ModelType, CreateSchemaType, UpdateSchemaType]
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
                self._model.full_url == value)
        elif short_url:
            statement = select(self._model).where(
                self._model.short_url == value and self._model.is_active)
        else:
            statement = select(self._model).where(self._model.id == value)
        results = await db.execute(statement=statement)

        return results.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip=0, limit=100
    ) -> list[ModelType]:
        """Get all objects"""

        statement = select(self._model).offset(skip).limit(limit)
        results = await db.execute(statement=statement)

        return results.scalars().all()

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
            db: AsyncSession,
            *,
            field: str,
            value: int | bool,
            id: int
    ) -> ModelType:
        """Update the object"""

        statement = select(self._model).where(self._model.id == id)
        results = await db.execute(statement=statement)
        db_obj = results.scalar_one_or_none()

        setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj
