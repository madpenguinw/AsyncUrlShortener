import logging
from typing import Any

import coloredlogs
from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api_logic.errors import (internal_server_error, url_gone_error,
                              url_not_found_error)
from api_logic.logic import get_client_address, shortener
from db.db import get_session
from schemas.entity import Url, UrlBase
from services.entity import click_crud, url_crud

router = APIRouter()

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


@router.post(
    '/',
    response_model=Url,
    status_code=status.HTTP_201_CREATED
)
async def create_short_url(
    *,
    db: AsyncSession = Depends(get_session),
    url_in: UrlBase,
    response: Response
) -> Any:
    """
    Create short version of URL.
    """

    if check_url := await url_crud.get(
            db=db, value=url_in.full_url, check=True):
        response.status_code = status.HTTP_302_FOUND

        logger.debug(
            'URL "%(full_url)s" is already in DB',
            {'full_url': url_in.full_url}
        )

        return check_url

    value = shortener()  # this is a short url

    url = await url_crud.create(
        db=db, field='short_url', value=value, obj_in=url_in
    )

    logger.debug(
        'URL "%(full_url)s" was successfully added to the DB',
        {'full_url': url_in.full_url}
    )

    return url


@router.post(
    '/batch',
    status_code=status.HTTP_201_CREATED
)
async def batch_url_upload(
    *,
    url_list: list[UrlBase],
    response: Response,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Upload a list of URLs to create a short version for each one.
    """

    try:
        result = await url_crud.create_multi(db=db, url_list=url_list)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='At least one of the submitted urls is already in database'
        )

    return result


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
) -> None:
    """
    Get short URL by ID and redirect. \n
    One can not see the redirection from Swagger. \n
    Make a request in a new browser page.
    """

    try:
        url_obj = await url_crud.update(
            id=url_id,
            field='clicks',
            db=db
        )
    except ValueError:
        logger.critical('Function got wrong args')
        internal_server_error()

    try:
        if not url_obj.is_active:
            logger.error(
                'Attempt to get deleted URL with ID="%(url_id)s"',
                {'url_id': url_id}
            )
            url_gone_error()

    except AttributeError:
        logger.error(
            'Url with ID="%(url_id)s" was not found in database',
            {'url_id': url_id}
        )
        url_not_found_error()

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
        'Click object with short URL "%(short_url)s" was created',
        {'short_url': url_obj.short_url}
    )

    response.headers['Location'] = url_obj.full_url

    logger.debug(
        'Client "%(client)s" was redirected',
        {'client': client}
    )

    return


@router.get(
    '/{url_id}/status',
    status_code=status.HTTP_200_OK,
    response_model=list | Url
)
async def get_url_info(
    url_id: int,
    db: AsyncSession = Depends(get_session),
    full_info: bool = False,
    max_result: int = 10,
    offset: int = 0
) -> Any:
    """
    Get URL usage status and Click objects.
    """

    url_obj = await url_crud.get(db=db, value=url_id)

    if not url_obj:
        # Код логеров я не могу вынести для переиспользования,
        # так как важно, в какой функции и в каком файле логгер срабатывает
        logger.error(
            'URL with ID="%(url_id)s" was not found in database',
            {'url_id': url_id}
        )
        url_not_found_error()

    elif not url_obj.is_active:
        logger.error(
            'Attempt to get deleted URL with ID="%(url_id)s"',
            {'url_id': url_id}
        )
        url_gone_error()

    if full_info:
        clicks = await click_crud.get_multi(
            url_id=url_obj.id, db=db, skip=offset, limit=max_result)
        return [url_obj, clicks]

    return url_obj


@router.delete(
    '/{url_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_url(
    *,
    db: AsyncSession = Depends(get_session),
    url_id: int,
) -> None:
    """
    Delete Url from database. \n
    In fact, this is a fake.
    """

    url_obj = await url_crud.update(
        id=url_id,
        field='is_active',
        db=db
    )

    if not url_obj:
        logger.error(
            'URL with ID="%(url_id)s" was not found in database',
            {'url_id': url_id}
        )
        url_not_found_error()

    logger.debug(
        'Short URL "%(short_url)s" was deleted',
        {'short_url': url_obj.short_url}
    )

    return
