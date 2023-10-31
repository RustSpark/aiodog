from typing import AsyncContextManager, List, Dict, Any, Optional


class Item:
    def __init__(
        self,
        manager: AsyncContextManager,
        data: Dict[str, Any],
        model_cls: Any,
        update_cols: Optional[List[str]] = None,
        message: Optional[str] = None,
    ):
        self._manager = manager
        self._data = data
        self._model_cls = model_cls
        self._update_cols = update_cols
        self._message = message

    @property
    def model_cls(self) -> Any:
        return self._model_cls

    @property
    def manager(self):
        return self._manager

    @property
    def message(self):
        return self._message
    
    @property
    def update_cols(self):
        return self._update_cols

    @property
    def data(self):
        return self._data
