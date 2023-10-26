import asyncio
import inspect
import traceback
from functools import wraps

from aiostream import operator, pipe, pipable_operator
from loguru import logger

from ._request import Request


class Control:
    def __init__(
        self,
        task_name: str,
        task_limit: int = 5,
    ):
        self._tn = task_name
        self._tl = task_limit

    def _execute(self):
        # @pipable_operator
        # def print_msg(source):
        #     def func(value):
        #         msg = f"Execute `{type(source).__name__}` successfully"
        #         if "msg" in value:
        #             msg += f': {value["msg"]}'
        #         if "callback" in value:
        #             msg += f', next execute {value["callback"].__name__}'
        #         msg += "!"
        #         logger.info(msg)
        #
        #     return stream.action.raw(source, func)

        @pipable_operator
        def wrapper(source):
            return (
                source
                # | print_msg.pipe()
                | pipe.map(self._recursive, task_limit=self._tl)
            )

        return wrapper

    async def _recursive(self, request: Request):
        await request.get_response()

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
