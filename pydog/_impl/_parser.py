import inspect
from functools import wraps


class Parser:
    def __init__(self, callback, *args):
        self._func = callback
        self._args = args

    def __call__(self, function):
        @wraps(function)
        async def wrapper(*args):
            if inspect.isawaitable(result := self._func(*self._args)):
                await result
            elif inspect.isasyncgen(result):
                async for request in result:
                    yield request
            if inspect.isawaitable(trans := function(*args)):
                await trans
            elif inspect.isasyncgen(trans):
                async for tran in trans:
                    yield tran

        return wrapper
