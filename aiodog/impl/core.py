import inspect
import os
import traceback
from functools import wraps
from typing import (
    Union,
    Tuple,
    Optional,
    TypeVar,
)

from aiostream import (
    operator,
    pipe,
)
from loguru import logger

from .base import _logger
from .buffer.item import Item, ItemBuffer
from .buffer.request import Request, RequestBuffer

_T = TypeVar("_T", Request, Item)


class Control:
    def __init__(
        self,
        task_name: str,
        task_limit: Optional[int] = min(32, (os.cpu_count() or 1) + 4),
        request_sleep_time: Optional[Union[Tuple, int]] = None,
        item_queue_maxsize: int = 1000,
        item_save_step_number: int = 5000,
    ):
        self._tn = task_name
        self._tl = task_limit
        self._request_buffer = RequestBuffer(
            sleep_time=request_sleep_time,
        )
        self._item_buffer = ItemBuffer(
            queue_maxsize=item_queue_maxsize,
            step_number=item_save_step_number,
        )

    async def _execute(self, function, *args):
        if inspect.iscoroutinefunction(function):
            await function(*args)
        elif inspect.isasyncgenfunction(function):
            await (
                operator(function)(*args)
                | _logger.pipe()
                | pipe.map(
                    self._callback,
                    task_limit=self._tl,
                    ordered=False,
                )
            )

    async def _callback(self, source: Optional[_T]):
        if hasattr(self, name := f"_{source.__class__.__name__.lower()}_buffer"):
            if hasattr(buffer := getattr(self, name), "start"):
                response = await buffer.start(source)
                if response is not None and (callback := source.callback):
                    await self._execute(callback, source, response)

    def __call__(self, function):
        @wraps(function)
        async def execute(*args):
            logger.info(f"Start execute task `{self._tn}`")
            async with self._item_buffer:
                try:
                    await self._execute(function, *args)
                except Exception:
                    logger.error(traceback.format_exc())

        return execute
