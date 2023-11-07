import asyncio
import inspect
import os
import random
from functools import wraps, partial
from typing import (
    Union,
    Tuple,
    Optional,
    TypeVar,
)

from aiostream import operator, pipe, core, async_
from loguru import logger

from .base import _logger
from .buffer.item import ItemBuffer
from .buffer.request import RequestBuffer
from .item import Item
from .request import Request

_T = TypeVar("_T", Request, Item)


class Control:
    def __init__(
        self,
        task_name: str,
        task_limit: Optional[int] = min(32, (os.cpu_count() or 1) + 4),
        request_sleep_time: Optional[Union[Tuple, int]] = None,
        request_queue_maxsize: int = 1000,
        item_queue_maxsize: int = 1000,
        item_save_step_number: int = 5000,
    ):
        self._tn = task_name
        self._tl = task_limit
        self._st = request_sleep_time
        self._request_queue = asyncio.Queue(maxsize=request_queue_maxsize)
        self._item_queue = asyncio.Queue(maxsize=item_queue_maxsize)
        self._request_buffer = RequestBuffer(
            queue=self._request_queue,
        )
        self._item_buffer = ItemBuffer(
            queue=self._item_queue,
            step_number=item_save_step_number,
        )
        self._task_number = 0

    async def _task(self, request: Request):
        try:
            function = request.func
            if isinstance(request.func, partial):
                function = getattr(request.func, "func")
                wrapped_function = partial(
                    function,
                    *getattr(request.func, "args"),
                    *request.func_args,
                    **getattr(request.func, "keywords"),
                    **request.func_kwargs,
                )
            else:
                wrapped_function = partial(
                    function,
                    *request.func_args,
                    **request.func_kwargs,
                )
            if inspect.ismethod(function):
                function = function.__func__
            if inspect.iscoroutinefunction(function):
                response = await wrapped_function()
            elif inspect.isasyncgenfunction(function):
                response = wrapped_function()
            else:
                response = await asyncio.to_thread(wrapped_function)
            if response is not None and (callback := request.callback):
                await self._put_queue(callback, request, response)
        except Exception as ex:
            logger.exception(ex)
        finally:
            self._task_number -= 1
            match self._st:
                case (a, b, *_):
                    await asyncio.sleep(random.uniform(a, b))
                case (a,) | a if isinstance(a, int):
                    await asyncio.sleep(a)

    async def _start(self):
        @operator
        async def run():
            while True:
                request = await self._request_queue.get()
                self._task_number += 1
                yield request

        try:
            await (
                run()
                | _logger.pipe()
                | pipe.map(
                    self._task,
                    task_limit=self._tl,
                )
            )
        except core.StreamEmpty:
            logger.error("")

    async def _put_queue(self, function, *args):
        if inspect.iscoroutinefunction(function):
            await function(*args)
        elif inspect.isasyncgenfunction(function):
            await (
                operator(function)(*args)
                | pipe.map(
                    async_(
                        lambda v: getattr(
                            self, f"_{v.__class__.__name__.lower()}_buffer"
                        ).put(v)
                    ),
                )
            )

    def __call__(self, function):
        @wraps(function)
        async def execute(*args):
            logger.info(f"Start execute task `{self._tn}`")
            async with self._item_buffer:
                try:
                    asyncio.create_task(self._start()),
                    await self._put_queue(function, *args)
                    while not self._request_queue.empty() or self._task_number:
                        await asyncio.sleep(0)
                except Exception as ex:
                    logger.exception(ex)

        return execute
