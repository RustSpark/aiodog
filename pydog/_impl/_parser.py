import inspect
from functools import wraps
from typing import Callable


class Parser:
    def __init__(self, callback: Callable, *args):
        self._func = callback
        self._args = args

    def __call__(self, function):
        @wraps(function)
        async def wrapper(*args):
            if inspect.isawaitable(result := self._func(*self._args)):
                await result
            elif inspect.isasyncgen(result):
                async for request_or_item in result:
                    yield request_or_item
            if inspect.isawaitable(trans := function(*args)):
                await trans
            elif inspect.isasyncgen(trans):
                async for tran in trans:
                    yield tran

        return wrapper
