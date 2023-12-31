import asyncio
from collections import defaultdict
from functools import partial
from typing import List

from aiostream import stream, pipe, pipable_operator, operator, streamcontext, core
from loguru import logger

from ..base import _logger
from ..item import Item


class ItemBuffer:
    def __init__(
        self,
        queue: asyncio.Queue,
        step_number: int = 5000,
    ):
        self._sn = step_number
        self._q = queue
        self._task = None
        self._sentinel = object()

    async def generate_items(self):
        async def combine_items(items: List[Item]) -> str:
            _cache = defaultdict(partial(defaultdict, partial(defaultdict, list)))
            for item in items:
                (_temp := _cache[item.manager][item.model_cls])["data"].append(
                    item.data
                )
                _temp["update_cols"] = item.update_cols
            tasks = []
            for m, mv in _cache.items():
                if hasattr(m, "add_batch"):
                    for t, tv in mv.items():
                        tasks.append(m.add_batch(t, tv))
            return f"Pipeline Result: [{await asyncio.gather(*tasks, return_exceptions=True)}]"

        @pipable_operator
        async def work(source):
            async with streamcontext(source) as streamer:
                async for count in streamer:
                    item = await self._q.get()
                    yield item
                    if (int(count) + 1) % self._sn == 0 or item is self._sentinel:
                        return

        @operator
        async def run():
            while True:
                items = await (stream.count() | work.pipe() | pipe.list())
                if self._sentinel is items[-1]:
                    items.pop()
                    if items:
                        yield items
                    break
                yield items

        try:
            await (run() | pipe.map(combine_items) | _logger.pipe())  # type: ignore
        except core.StreamEmpty:
            logger.warning("No Items Exists!")

    async def put(self, item: Item):
        await self._q.put(item)

    async def __aenter__(self):
        self._task = asyncio.create_task(self.generate_items())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._q.put(self._sentinel)
        if self._task:
            await self._task
