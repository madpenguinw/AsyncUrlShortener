from models.entity import Url as UrlModel
from schemas.entity import Url, UrlBase

from .base import RepositoryDB


class RepositoryUrl(RepositoryDB[UrlModel, UrlBase, Url]):
    pass


url_crud = RepositoryUrl(UrlModel)
