from models.entity import Click as ClickModel
from models.entity import Url as UrlModel
from schemas.entity import ClickInfo, Url, UrlBase

from .base import ClickCRUD, UrlCRUD


class RepositoryUrl(UrlCRUD[UrlModel, UrlBase, Url]):
    pass


class RepositoryClick(ClickCRUD[ClickModel, ClickInfo]):
    pass

url_crud = RepositoryUrl(UrlModel)
click_crud = RepositoryClick(ClickModel)
