import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = "postgresql+psycopg2://user:password@localhost:5432/postgres"
    secret_key: str = "secret_key"
    algorithm: str = "HS256"
    huggingfacehub_api_token: str = "123"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = settings.huggingfacehub_api_token
