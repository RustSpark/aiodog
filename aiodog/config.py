from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # sqlalchemy
    engine_echo: bool = False
    fetch_step: int = 1000

    # aiohttp
    random_useragent: bool = True
    default_useragent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
    )

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache
def _get_settings():
    return Settings()


settings = _get_settings()
