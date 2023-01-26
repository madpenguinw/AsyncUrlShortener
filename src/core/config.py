import os
from logging import config as logging_config

from pydantic import BaseSettings, PostgresDsn

from core.logger import LOGGING

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging_config.dictConfig(LOGGING)

PROJECT_NAME = os.getenv('PROJECT_NAME', 'url_shortener')
PROJECT_HOST = os.getenv('PROJECT_HOST', '0.0.0.0')
PROJECT_PORT = int(os.getenv('PROJECT_PORT', '8000'))


class AppSettings(BaseSettings):
    app_title: str = 'UrlShortener'
    database_dsn: PostgresDsn

    class Config:
        env_file = '.env'


app_settings = AppSettings()
