from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # sqlalchemy
    engine_echo: bool = False

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache
def _get_settings():
    return Settings()


settings = _get_settings()
