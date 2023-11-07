import asyncio
from ..request import Request


class RequestBuffer:
    def __init__(
        self,
        queue: asyncio.Queue,
    ):
        self._q = queue

    async def put(self, request: Request):
        await self._q.put(request)
