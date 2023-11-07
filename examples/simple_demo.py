import asyncio

from aiodog import Control, Request


async def test():
    await asyncio.sleep(1)
    return 1


def main():
    async def wrap():
        @Control(task_name="Just Test")
        async def run():
            for _ in range(2):
                yield Request(function=test, callback=echo)

        async def echo(request, response):
            print(response)

        await run()

    asyncio.run(wrap())


if __name__ == "__main__":
    main()
