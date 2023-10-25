import asyncio
from pydog import Control, Parser


def main():
    async def parser2(a):
        for i in range(2):
            print(2)
            yield {f"2-{i}": a}

    async def parser3(b):
        for i in range(2):
            print(3)
            yield {f"3-{i}": b}

    @Control(task_name="simple demo")
    @Parser(parser2, 1)
    @Parser(parser3, 2)
    async def run(c):
        print("just test", c)
        yield {}

    asyncio.run(run(3))


if __name__ == "__main__":
    main()
