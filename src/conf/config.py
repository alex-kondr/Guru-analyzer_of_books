import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = "postgresql+psycopg2://user:password@localhost:5432/postgres"
    secret_key: str = "secret_key"
    algorithm: str = "HS256"
    hugginfacehub_api_token = "123"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = settings.hugginfacehub_api_token
