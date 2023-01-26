from models.entity import Url as UrlModel, Click as ClickModel
from schemas.entity import Url, UrlBase, ClickInfo

from .base import RepositoryDB


class RepositoryUrl(RepositoryDB[UrlModel, UrlBase, Url]):
    pass


class RepositoryClick(RepositoryDB[ClickModel, ClickInfo, ClickInfo]):
    pass


url_crud = RepositoryUrl(UrlModel)

click_crud = RepositoryClick(ClickInfo)
