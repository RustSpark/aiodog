from typing import Any, Callable, Dict, Optional, Tuple


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
