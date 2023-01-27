import logging

import coloredlogs
from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from sqlalchemy.ext.asyncio import AsyncSession

from api_logic.logic import get_client_address
from db.db import get_session
from services.entity import click_crud, url_crud

from .entity import router

api_router = APIRouter()
api_router.include_router(router, prefix='/urls', tags=['General Methods'])
local_router = APIRouter()

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


@local_router.get(
    '/{short_url}',
    status_code=status.HTTP_307_TEMPORARY_REDIRECT
)
async def url_following(
    short_url: str,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """
    Get short url and redirect user to the
    needed resource using full url from db. \n
    This function doesn't work from Swagger.
    """

    url_obj = await url_crud.get(
        db=db, value=short_url, short_url=True)

    if not url_obj:
        logger.error(
            'Short URL "%(short_url)s" was not found in database',
            {'short_url': short_url}
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Url not found'
        )

    await url_crud.update(
        id=url_obj.id,
        field='clicks',
        db=db
    )

    logger.debug(
        'Short URL "%(short_url)s" was used',
        {'short_url': short_url}
    )

    client = get_client_address(
        request=request
    )

    await click_crud.create(
        url_id=url_obj.id, client=client, db=db)

    logger.debug(
        'Click object with short url "%(short_url)s" was created',
        {'short_url': short_url}
    )

    response.headers['Location'] = url_obj.full_url

    logger.debug(
        'Client "%(client)s" was redirected',
        {'client': client}
    )

    return

api_router.include_router(local_router, tags=['Redirect using short url'])
