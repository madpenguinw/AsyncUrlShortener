from datetime import datetime
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from models.entity import Click
from schemas import entity as model_schema


async def create_click_obj(
    url_id: int,
    client: str,
    db: AsyncSession = Depends(get_session)
) -> None:
    """Create Click object."""

    click_obj: model_schema.ClickInfo = Click(
        url_id=url_id,
        date=datetime.now(),
        client=client
    )

    db.add(click_obj)
    await db.commit()
    await db.refresh(click_obj)
    return


async def add_click(
    url_obj: model_schema.Url,
    db: AsyncSession = Depends(get_session),
) -> None:
    """Increment "click" value."""

    clicks = url_obj.clicks + 1
    setattr(url_obj, 'clicks', clicks)

    db.add(url_obj)
    await db.commit()
    await db.refresh(url_obj)
    return


def get_client_address(request: Request) -> str:
    """Get client's addres."""

    client: str = request.client.host + ':' + \
        str(request.client.port)
    print(f'{client = }')
    return client
