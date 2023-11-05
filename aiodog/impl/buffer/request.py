import asyncio
import inspect
import random
import traceback
from functools import partial
from typing import Any, Callable, Dict, Optional, Tuple, Union

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

    @property
    def func(self):
        return self._func

    @property
    def func_args(self):
        return self._func_args

    @property
    def func_kwargs(self):
        return self._func_kwargs


class RequestBuffer:
    def __init__(
        self,
        sleep_time: Optional[Union[int, Tuple]] = None,
    ):
        self._st = sleep_time

    async def start(self, request: Request) -> Optional[Any]:
        if not request.func:
            return
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
                    function, *request.func_args, **request.func_kwargs
                )
            if inspect.ismethod(function):
                function = function.__func__
            if inspect.iscoroutinefunction(function):
                return await wrapped_function()
            elif inspect.isasyncgenfunction(function):
                return wrapped_function()
            else:
                return await asyncio.to_thread(wrapped_function)
        except Exception:
            logger.error(traceback.format_exc())
        finally:
            match self._st:
                case (a, b, *_):
                    await asyncio.sleep(random.uniform(a, b))
                case (a,) | a if isinstance(a, int):
                    await asyncio.sleep(a)