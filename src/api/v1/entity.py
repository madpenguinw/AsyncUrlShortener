import logging
from typing import Any

import coloredlogs
from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from sqlalchemy.ext.asyncio import AsyncSession

from api_logic.logic import get_client_address, shortener
from db.db import get_session
from schemas import entity as model_schema
from services.entity import click_crud, url_crud

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
    Create short version of url.
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


@router.get(
    '/{url_id}',
    status_code=status.HTTP_307_TEMPORARY_REDIRECT
)
async def get_url(
    *,
    db: AsyncSession = Depends(get_session),
    url_id: int,
    response: Response,
    request: Request
) -> Any:
    """
    Get short url by ID and redirect. \n
    This function doesn't work from Swagger.
    """

    url_obj = await url_crud.get(db=db, value=url_id)
    if not url_obj:
        logger.error(
            'URL with id="%(url_id)s" was not found in database',
            {'url_id': url_id}
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Url not found'
        )

    await url_crud.update(
        id=url_id,
        field='clicks',
        db=db
    )

    logger.debug(
        'Short URL "%(short_url)s" was used',
        {'short_url': url_obj.short_url}
    )

    client = get_client_address(
        request=request
    )

    await click_crud.create(
        url_id=url_id, client=client, db=db)

    logger.debug(
        'Click object with short url "%(short_url)s" was created',
        {'short_url': url_obj.short_url}
    )

    response.headers['Location'] = url_obj.full_url

    logger.debug(
        'Client "%(client)s" was redirected',
        {'client': client}
    )

    return

# @router.post('/', response_model=list[model_schema.Entity])
# async def read_entities(
#     db: AsyncSession = Depends(get_session), skip: int = 0, limit: int = 100
# ) -> Any:
#     """
#     Retrieve entities.
#     """
#     # get entities from db
#     entities = await model_crud.get_multi(db=db, skip=skip, limit=limit)
#     return entities




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
