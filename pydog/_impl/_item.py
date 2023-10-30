from typing import AsyncContextManager, List, Dict, Any, Optional


class Item:
    def __init__(
        self,
        manager: AsyncContextManager,
        data: Dict[str, Any],
        table_name: str,
        update_cols: Optional[List[str]] = None,
        message: Optional[str] = None,
    ):
        self._manager = manager
        self._data = data
        self._table_name = table_name
        self._update_cols = update_cols
        self._message = message
