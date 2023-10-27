import asyncio
import inspect
import traceback
from typing import Callable, Tuple, Dict, Any

from aiohttp import ClientSession

from ._response import Response


class Request:
    def __init__(
        self,
        function: Callable = None,
        function_args: Tuple = None,
        function_kwargs: Dict[str, Any] = None,
        callback: Callable = None,
        message: str = None,
        transform: Any = None,
    ):
        self._func = function
        self._func_args = function_args or tuple()
        self._func_kwargs = function_kwargs or dict()
        self._callback = callback
        self._msg = message
        self._trans = transform

    @property
    def callback(self):
        return self._callback

    @property
    def msg(self):
        return self._msg

    @property
    def trans(self):
        return self._trans

    async def get_response(self):
        try:
            function = self._func
            if inspect.ismethod(self._func):
                function = getattr(self._func, "__func__")
                if isinstance(
                    instance := getattr(self._func, "__self__"), ClientSession
                ):
                    return
                    # async with self._func(*self._func_args, **self._func_kwargs) as res:
                    #     pass
            if inspect.iscoroutinefunction(function):
                await self._func(*self._func_args, **self._func_kwargs)
            elif inspect.isasyncgenfunction(function):
                self._func(*self._func_args, **self._func_kwargs)
            else:
                await asyncio.to_thread(
                    self._func, *self._func_args, **self._func_kwargs
                )
        except Exception:
            traceback.print_exc()
