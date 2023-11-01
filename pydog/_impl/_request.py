import asyncio
import inspect
import random
import traceback
from typing import Any, Callable, Dict, Optional, Tuple, Union

from aiohttp import ClientSession
from loguru import logger

from ..config import settings


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


class RequestBuffer:
    def __init__(
        self,
        sleep_time: Optional[Union[int, Tuple]] = None,
    ):
        self._st = sleep_time

    async def start(self, request: Request) -> Optional[Tuple[Request, Any]]:
        if not request._func:
            return
        try:
            function = request._func
            if inspect.ismethod(request._func):
                function = getattr(request._func, "__func__")
                if isinstance(
                    instance := getattr(request._func, "__self__"), ClientSession
                ):
                    async with request._func(
                        *request._func_args, **request._func_kwargs
                    ) as res:
                        return request, res
            if inspect.iscoroutinefunction(function):
                return request, await request._func(
                    *request._func_args, **request._func_kwargs
                )
            elif inspect.isasyncgenfunction(function):
                return request, request._func(
                    *request._func_args, **request._func_kwargs
                )
            else:
                return request, await asyncio.to_thread(
                    request._func, *request._func_args, **request._func_kwargs
                )
        except Exception:
            logger.error(traceback.format_exc())
        finally:
            match self._st:
                case (a, b, *_):
                    await asyncio.sleep(random.uniform(a, b))
                case (a,) | a if isinstance(a, int):
                    await asyncio.sleep(a)
