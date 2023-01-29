import os

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn

load_dotenv()


class AppSettings(BaseSettings):
    title: str = os.environ.get('PROJECT_NAME', 'UrlShortener')
    host: str = os.environ.get('PROJECT_HOST', '127.0.0.1')
    port: int = int(os.environ.get('PROJECT_PORT', 8080))
    blacklisted_ips: list[str, None] = os.environ.get('BLACKLISTED_IPS', [])
    database_dsn: PostgresDsn

    class Config:
        env_file = '.env'


app_settings = AppSettings()
