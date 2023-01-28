import os

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn


load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_NAME = os.environ.get('PROJECT_NAME', 'UrlShortener')
PROJECT_HOST = os.environ.get('PROJECT_HOST', '127.0.0.1')
PROJECT_PORT = int(os.environ.get('PROJECT_PORT', 8080))

BLACKLISTED_IPS = os.environ.get('BLACKLISTED_IPS', [])


class AppSettings(BaseSettings):
    app_title: str = PROJECT_NAME
    database_dsn: PostgresDsn

    class Config:
        env_file = '.env'


app_settings = AppSettings()
