from functools import partial
from typing import Any, Optional

from aiohttp import ClientSession
from aiohttp.hdrs import METH_ALL
from aiohttp.typedefs import StrOrURL

from ..response.spider import AIOHttpResponse


class ASpiderSession(ClientSession):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __getattribute__(self, item: str):
        if (method := item.upper()) in METH_ALL:
            return partial(
                super().__getattribute__("_get_response"),
                method,
            )
        else:
            return super().__getattribute__(item)

    async def _get_response(
        self, method: str, url: StrOrURL, **kwargs: Any
    ) -> Optional[AIOHttpResponse]:
        async with self.request(
            method=method,
            url=url,
            **kwargs,
        ) as response:
            return await AIOHttpResponse(response).assignment()
