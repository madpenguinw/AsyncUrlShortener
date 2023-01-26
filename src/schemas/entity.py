from datetime import datetime

from pydantic import BaseModel, HttpUrl


class UrlBase(BaseModel):
    """Shared url properties"""
    full_url: HttpUrl


class Url(UrlBase):
    """Full url properties in DB"""
    id: int
    short_url: str
    clicks: int
    is_active: bool

    class Config:
        orm_mode = True


class ClickInfo(BaseModel):
    """Information about certain url click"""
    id: int
    url_id: int
    date: datetime
    client: str

    class Config:
        orm_mode = True
