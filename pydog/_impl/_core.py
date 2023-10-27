import asyncio
import inspect
import traceback
from functools import wraps
from typing import Union

from aiostream import operator, pipe, pipable_operator
from loguru import logger

from ._request import Request
from ._item import Item


class Control:
    def __init__(
        self,
        task_name: str,
        task_limit: int = 5,
    ):
        self._tn = task_name
        self._tl = task_limit

    def _execute(self):
        @pipable_operator
        def wrapper(source):
            return source | pipe.map(self._recursive, task_limit=self._tl)

        return wrapper

    async def _recursive(self, request_or_item: Union[Request, Item]):
        if isinstance(request_or_item, Item):
            pass
        elif isinstance(request_or_item, Request):
            response = await request_or_item.get_response()
            if response and (callback := request_or_item.callback):
                if inspect.iscoroutinefunction(callback):
                    await callback(request_or_item, response)
                elif inspect.isasyncgenfunction(callback):
                    await (
                        operator(callback)(request_or_item, response) | self._execute()
                    )

    def __call__(self, function):
        @wraps(function)
        async def wrapper(*args):
            logger.info(f"Start execute task `{self._tn}`")
            try:
                if inspect.iscoroutinefunction(function):
                    await function(*args)
                elif inspect.isasyncgenfunction(function):
                    await (operator(function)(*args) | self._execute())
            except Exception:
                traceback.print_exc()

        return wrapper
