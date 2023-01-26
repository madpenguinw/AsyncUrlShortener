import coloredlogs
import logging

from fastapi import APIRouter, Depends, Response, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from logic.click import create_click_obj, get_client_address, add_click

from services.entity import url_crud

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

    await add_click(
        url_obj=url_obj,
        db=db
    )

    logger.debug(
        'Short URL "%(short_url)s" was used',
        {'short_url': short_url}
    )

    client = get_client_address(
        request=request
    )

    await create_click_obj(
        url_id=url_obj.id,
        client=client,
        db=db,
    )

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


# class CollectionUrl(BaseModel):
#     full_url: str


# @api_router.post('/', response_model=CollectionUrl)
# async def create_url(url: CollectionUrl):
#     return url


# @api_router.get('/info')
# async def info_handler():
#     return {
#         'api': 'v1',
#         'python': sys.version_info
#     }


# @api_router.get('/filter')
# async def filter_handler(param1: str, param2: int|None = None) -> dict[str, str|int|None]:
#     return {
#         'action': 'filter',
#         'param1': param1,
#         'param2': param2
#     }


# @api_router.get("/xml-data/")
# def get_legacy_data():
#     data = """<?xml version="1.0" encoding="UTF-8"?>
#     <note>
#       <to>Tove</to>
#       <from>Jani</from>
#       <heading>Reminder</heading>
#       <body>Don't forget me this weekend!</body>
#     </note>
#     """
#     return Response(content=data, media_type="application/xml")
