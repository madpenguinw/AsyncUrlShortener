from datetime import datetime

from pydantic import BaseModel, HttpUrl


class Settings(BaseModel):
    class Config:
        orm_mode = True


class UrlBase(BaseModel):
    """Shared url properties"""
    full_url: HttpUrl


class Url(UrlBase, Settings):
    """Full url properties in DB"""
    id: int
    short_url: str
    clicks: int
    is_active: bool


class ClickInfo(Settings):
    """Information about certain url click"""
    id: int
    url_id: int
    date: datetime
    client: str
