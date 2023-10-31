from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    engine_echo: bool = False

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache
def get_settings():
    return Settings()
