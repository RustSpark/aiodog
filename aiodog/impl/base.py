from typing import AsyncIterator, AsyncIterable

from aiostream import pipable_operator, stream
from loguru import logger


@pipable_operator
def _logger(source: AsyncIterable) -> AsyncIterator:
    def message(value) -> None:
        if hasattr(value, "msg") and (msg := value.msg):
            logger.info(msg)
        elif isinstance(value, str):
            logger.info(value)

    return stream.action.raw(source, message)


async def _callback():
    pass
