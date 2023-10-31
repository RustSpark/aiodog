import sys
import traceback
from asyncio import current_task

from loguru import logger
from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
    AsyncSession,
)
from sqlalchemy.ext.declarative import declarative_base

from ..config import get_settings


Base = declarative_base()


class Pipeline:
    def __init__(self, name: str) -> None:
        try:
            self._engine: AsyncEngine = create_async_engine(
                getattr(settings := get_settings(), name, ""),
                echo=settings.engine_echo,
            )
        except Exception:
            logger.error(traceback.format_exc())
            sys.exit(1)

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    def get_session(self) -> AsyncSession:
        return async_scoped_session(
            async_sessionmaker(
                bind=self._engine,
                autoflush=False,
                expire_on_commit=False,
            ),
            scopefunc=current_task,
        )()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._engine.dispose()

    async def find_one(self, statement, **kwargs):
        async with self.get_session() as session:
            return (await session.execute(statement, **kwargs)).scalar_one_or_none()

    async def find_all(self, statement, **kwargs):
        async with self.get_session() as session:
            return (await session.execute(statement, **kwargs)).scalars().all()

    async def transaction(self, statement, **kwargs):
        async with self.get_session() as session:
            async with session.begin():
                await session.execute(statement, **kwargs)
            await session.commit()
