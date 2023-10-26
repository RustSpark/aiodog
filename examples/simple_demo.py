import asyncio
import time

from aiohttp import ClientSession

from pydog import Control, Parser, Request


def main():
    async def wrapper():
        async with ClientSession() as session:

            class RequestCls:
                @classmethod
                async def request_async_cls_method(cls):
                    await asyncio.sleep(2)

                @classmethod
                def request_sync_cls_method(cls):
                    print(">>>>>>")

                @staticmethod
                async def request_async_static_function():
                    await asyncio.sleep(2)

                @staticmethod
                def request_sync_static_function():
                    print("=====>")

            async def request_function():
                await asyncio.sleep(1)

            async def parser2(a):
                for i in range(2):
                    yield Request(
                        function=session.get,
                    )

            async def parser3(b):
                for i in range(2):
                    yield Request(
                        function=request_function,
                    )

            @Control(task_name="simple demo")
            @Parser(parser2, 1)
            @Parser(parser3, 2)
            async def run(c):
                yield Request(
                    function=RequestCls.request_sync_cls_method,
                )
                yield Request(
                    function=RequestCls.request_async_cls_method,
                )
                yield Request(
                    function=RequestCls.request_async_static_function,
                )
                yield Request(
                    function=RequestCls.request_sync_static_function,
                )

            await run(3)

    asyncio.run(wrapper())


if __name__ == "__main__":
    main()
