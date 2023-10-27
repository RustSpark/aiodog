import asyncio
import inspect
import traceback
from typing import Any, Callable, Dict, Optional, Tuple

from aiohttp import ClientSession
from loguru import logger


class Request:
    def __init__(
        self,
        function: Optional[Callable] = None,
        function_args: Optional[Tuple] = None,
        function_kwargs: Optional[Dict[str, Any]] = None,
        callback: Optional[Callable] = None,
        message: Optional[str] = None,
        transform: Any = None,
    ):
        self._func = function
        self._func_args = function_args or ()
        self._func_kwargs = function_kwargs or {}
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
        if not self._func:
            return
        try:
            function = self._func
            if inspect.ismethod(self._func):
                function = getattr(self._func, "__func__")
                if isinstance(
                    instance := getattr(self._func, "__self__"), ClientSession
                ):
                    async with self._func(*self._func_args, **self._func_kwargs) as res:
                        return res
            if inspect.iscoroutinefunction(function):
                return await self._func(*self._func_args, **self._func_kwargs)
            elif inspect.isasyncgenfunction(function):
                return self._func(*self._func_args, **self._func_kwargs)
            else:
                return await asyncio.to_thread(
                    self._func, *self._func_args, **self._func_kwargs
                )
        except Exception:
            logger.error(traceback.format_exc())
