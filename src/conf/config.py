import os

from pydantic import BaseSettings

os.system("python3 -m spacy download en_core_web_sm")
os.system("py -m spacy download en_core_web_sm")

class Settings(BaseSettings):
    sqlalchemy_database_url: str = "postgresql+psycopg2://user:password@localhost:5432/postgres"
    secret_key: str = "secret_key"
    algorithm: str = "HS256"
    huggingfacehub_api_token: str = "123"
    openai_api_key: str = "123"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
