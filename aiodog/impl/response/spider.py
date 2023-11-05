import traceback
from typing import Optional, Any

from aiohttp import ClientResponse
from loguru import logger
from parsel import Selector


class AIOHttpResponse:
    def __init__(self, response: ClientResponse) -> None:
        self._response = response
        self._text: Optional[str] = None
        self._content: Optional[bytes] = None
        self._json: Any = None
        self._selector: Optional[Selector] = None

    @property
    def text(self):
        return self._text

    @property
    def headers(self):
        return self._response.headers

    @property
    def cookies(self):
        return self._response.cookies

    @property
    def content_type(self):
        return self._response.content_type

    @property
    def status(self):
        return self._response.status

    @property
    def content(self):
        return self._content

    @property
    def json(self):
        return self._json

    @property
    def selector(self):
        return self._selector

    async def assignment(
        self,
    ) -> "AIOHttpResponse":
        try:
            content_type = self._response.content_type
            if content_type == "text/html":
                self._text = await self._response.text()
                self._selector = Selector(self._text)
            elif content_type == "application/json":
                self._json = await self._response.json()
            else:
                self._content = await self._response.read()
        except Exception:
            logger.error(traceback.format_exc())
        return self
