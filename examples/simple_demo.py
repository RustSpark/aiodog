import asyncio
import random

from loguru import logger

from aiodog import Control, Request


async def test():
    await asyncio.sleep(random.uniform(3, 6))
    return 1


def main():
    async def wrap():
        async def run2():
            print("===>")
            # yield Request(function=test, callback=echo)

        @Control(task_name="Just Test")
        # @Parser(callback=run2)
        async def run():
            for _ in range(10):
                yield Request(function=test, callback=echo, message=f"run_{_}")
            # yield Request(function=test, callback=echo2)

        async def echo(request, response):
            for _ in range(10):
                yield Request(function=test, callback=echo2, message=f"{request.msg} echo_{_}")

        async def echo2(request, response):
            logger.info(request.msg)

        await run()

    asyncio.run(wrap())


if __name__ == "__main__":
    main()
