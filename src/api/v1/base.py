import coloredlogs
import logging

from datetime import datetime
from fastapi import APIRouter, Depends, Response, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import entity as model_schema

from core.logger import LOGGING
from db.db import get_session
from models.entity import Click
from services.entity import url_crud, click_crud

from .entity import router

api_router = APIRouter()
api_router.include_router(router, prefix='/urls', tags=['General Methods'])
local_router = APIRouter()

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


@local_router.get(
    '/{short_url}',
    response_class=RedirectResponse
)
async def url_following(
    short_url: str,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """
    Get short url and connect user to the
    needed resource using full url from db. \n
    This function doesn't work from Swagger.
    """

    full_url = await url_crud.get(
        db=db, value=short_url, short_url=True)

    if full_url:
        clicks = full_url.clicks + 1
        setattr(full_url, 'clicks', clicks)

        db.add(full_url)
        await db.commit()
        await db.refresh(full_url)

        logger.debug(
            'Short URL "%(short_url)s" was used',
            {'short_url': short_url}
        )

        client: str = request.client.host + ':' + \
            str(request.client.port)

        click_obj = Click(
            url_id=full_url.id,
            date=datetime.now(),
            client=client
        )

        db.add(click_obj)
        await db.commit()
        await db.refresh(click_obj)

        logger.debug(
            'Click object with short url "%(short_url)s" was created',
            {'short_url': short_url}
        )

        logger.debug(
            'Client "%(client)s" was redirected',
            {'client': client}
        )

        return RedirectResponse(full_url.full_url)

    else:
        logger.error(
            'Short URL "%(short_url)s" was not found in database',
            {'short_url': short_url}
        )
        response.status_code = status.HTTP_404_NOT_FOUND

        return


api_router.include_router(local_router, tags=['Follow The Short Url'])


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