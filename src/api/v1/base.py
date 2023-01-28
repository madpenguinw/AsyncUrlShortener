import asyncio
import logging

import coloredlogs
from async_timeout import timeout
from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from api_logic.logic import get_client_address
from db.db import get_session
from models.entity import Click as ClickModel
from models.entity import Url as UrlModel
from services.entity import click_crud, url_crud

from .entity import router

api_router = APIRouter()
api_router.include_router(router, prefix='/urls', tags=['General Methods'])
local_router = APIRouter()

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


@local_router.get(
    '/ping',
    status_code=status.HTTP_200_OK
)
async def ping_database(
    db: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """
    Check if the database is available.
    """

    try:
        async with timeout(1):
            await asyncio.gather(
                db.execute(select(UrlModel)),
                db.execute(select(ClickModel))
            )
    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Database is not available'
        )
    return {'detail': 'Database is available'}


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
    Get short URL and redirect user to the
    needed resource using full URL from db. \n
    One can not see the redirection from Swagger. \n
    Make a request in a new browser page.
    """

    url_obj = await url_crud.get(
        db=db, value=short_url, short_url=True)

    if not url_obj:
        logger.error(
            'Short URL "%(short_url)s" was not found in database',
            {'short_url': short_url}
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='URL not found'
        )

    elif not url_obj.is_active:
        logger.error(
            'Attempt to get deleted URL with ID="%(id)s"',
            {'id': url_obj.id}
        )
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail='URL was deleted from the database.'
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
        'Click object with short URL "%(short_url)s" was created',
        {'short_url': short_url}
    )

    response.headers['Location'] = url_obj.full_url

    logger.debug(
        'Client "%(client)s" was redirected',
        {'client': client}
    )

    return

api_router.include_router(local_router, tags=['Other methods'])
