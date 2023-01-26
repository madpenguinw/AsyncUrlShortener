import coloredlogs
import logging

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from logic.url_shortener import shortener
from schemas import entity as model_schema
from services.entity import url_crud

router = APIRouter()

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


@router.post(
    '/',
    response_model=model_schema.Url,
    status_code=status.HTTP_201_CREATED
)
async def create_short_url(
    *,
    db: AsyncSession = Depends(get_session),
    url_in: model_schema.UrlBase,
    response: Response
) -> Any:
    """
    Gets full url and creates its short version.
    """

    check_url = await url_crud.get(
        db=db, value=url_in.full_url, check=True)
    if check_url:
        response.status_code = status.HTTP_302_FOUND
        logger.debug(
            'URL "%(full_url)s" is already in DB',
            {'full_url': url_in.full_url}
        )
        return check_url

    value = shortener()  # this is short url

    url = await url_crud.create(
        db=db, field='short_url', value=value, obj_in=url_in
    )

    logger.debug(
        'URL "%(full_url)s" was successfully added to the DB',
        {'full_url': url_in.full_url}
    )

    return url

# @router.post('/', response_model=list[model_schema.Entity])
# async def read_entities(
#     db: AsyncSession = Depends(get_session), skip: int = 0, limit: int = 100
# ) -> Any:
#     """
#     Retrieve entities.
#     """
#     # get entities from db
#     entities = await entity_crud.get_multi(db=db, skip=skip, limit=limit)
#     return entities


# @router.get("/{id}", response_model=entity_schema.Entity)
# async def read_entity(
#     *,
#     db: AsyncSession = Depends(get_session),
#     id: int,
# ) -> Any:
#     """
#     Get by ID.
#     """
#     # get entity from db
#     entity = await entity_crud.get(db=db, id=id)
#     if not entity:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
#         )
#     return entity

# @router.put('/{id}', response_model=entity_schema.Entity)
# async def update_entity(
#     *,
#     db: AsyncSession = Depends(get_session),
#     id: int,
#     entity_in: entity_schema.EntityUpdate,
# ) -> Any:
#     """
#     Update an entity.
#     """
#     # get entity from db
#     entity = await entity_crud.get(db=db, id=id)

#     if not entity:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')

#     # update entity in db
#     entity_out = await entity_crud.update(db=db, db_obj=entity, obj_in=entity_in)

#     return entity_out


# @router.delete('/{id}', response_model=entity_schema.Entity)
# async def delete_entity(
#     *, db: AsyncSession = Depends(get_session), id: int
# ) -> Any:
#     """
#     Delete an entity.
#     """
#     entity = {}
#     # get entity from db
#     entity = await entity_crud.get(db=db, id=id)

#     if not entity:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='Item not found'
#         )

#     # remove item from db
#     entity = await entity_crud.delete(db=db, id=id)

#     return entity
