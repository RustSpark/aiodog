import asyncio
import inspect
import random
import traceback
from asyncio import Queue
from collections import defaultdict
from functools import wraps, partial
from typing import Union, Tuple, Optional, List, AsyncIterator, AsyncIterable

from aiostream import (
    operator,
    pipe,
    pipable_operator,
    streamcontext,
    stream,
    core,
    async_,
)
from loguru import logger

from ._request import Request
from ._item import Item


@pipable_operator
def _logger(source: AsyncIterable) -> AsyncIterator:
    def message(value) -> None:
        if type(value) == str:
            logger.info(value)

    return stream.action.raw(source, message)


class Control:
    def __init__(
        self,
        task_name: str,
        task_limit: int = 5,
        task_sleep_time: Optional[Union[Tuple, int]] = None,
        pipeline_limit: int = 5,
        item_queue_maxsize: int = 1000,
        item_save_step_number: int = 5000,
    ):
        self._tn = task_name
        self._tl = task_limit
        self._tst = task_sleep_time
        self._pl = pipeline_limit
        self._q = Queue(maxsize=item_queue_maxsize)
        self._isn = item_save_step_number
        self._sentinel = object()

    def _execute(self):
        @pipable_operator
        def wrapper(source):
            return (
                source | _logger.pipe() | pipe.map(self._recursive, task_limit=self._tl)  # type: ignore
            )

        return wrapper

    def _assign_items(self, items: List[Item]):
        _cache = defaultdict(partial(defaultdict, partial(defaultdict, list)))
        for item in items:
            (_temp := _cache[item.manager][item.model_cls])["data"].append(item.data)
            _temp["update_cols"] = item.update_cols
        for m, mv in _cache.items():
            if hasattr(m, "add_batch"):
                for t, tv in mv.items():
                    yield partial(getattr(m, "add_batch"), t, tv)

    async def _async_generate_items(self):
        @pipable_operator
        async def wrapper(source):
            async with streamcontext(source) as streamer:
                async for count in streamer:
                    item = await self._q.get()
                    yield item
                    if (count + 1) % self._isn == 0 or item is self._sentinel:
                        return

        @operator
        async def runner():
            while True:
                items = await (stream.count() | wrapper.pipe() | pipe.list())
                if self._sentinel is items[-1]:
                    items.pop()
                    if items:
                        for source in self._assign_items(items):
                            yield source
                    break
                for source in self._assign_items(items):
                    yield source

        try:
            await (
                runner()
                | pipe.map(
                    async_(lambda source: source()),  # type: ignore
                    task_limit=self._pl,
                )
                | _logger.pipe()
            )
        except core.StreamEmpty:
            logger.warning("No items exists!")

    async def _recursive(self, request_or_item: Union[Request, Item]):
        if isinstance(request_or_item, Item):
            await self._q.put(request_or_item)
        elif isinstance(request_or_item, Request):
            response = await request_or_item.get_response()
            match self._tst:
                case (a, b, *_):
                    await asyncio.sleep(random.uniform(a, b))
                case (a,) | a if isinstance(a, int):
                    await asyncio.sleep(a)
            if response and (callback := request_or_item.callback):
                if inspect.iscoroutinefunction(callback):
                    await callback(request_or_item, response)
                elif inspect.isasyncgenfunction(callback):
                    await (
                        operator(callback)(request_or_item, response) | self._execute()
                    )

    def __call__(self, function):
        @wraps(function)
        async def execute(*args):
            logger.info(f"Start execute task `{self._tn}`")
            task = None
            try:
                task = asyncio.create_task(self._async_generate_items())
                if inspect.iscoroutinefunction(function):
                    await function(*args)
                elif inspect.isasyncgenfunction(function):
                    await (operator(function)(*args) | self._execute())
            except Exception:
                logger.error(traceback.format_exc())
            finally:
                await self._q.put(self._sentinel)
                if task:
                    await task

        return execute
