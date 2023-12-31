import asyncio

from loguru import logger
from sqlalchemy import select

from examples.model import T1
from aiodog import MysqlPipeline, Control, Request, Item


def main():
    async def wrap():
        async with MysqlPipeline("mysql") as pipeline:
            # for _ in range(100):
            #     logger.info(await pipeline.find_one(select(T1).where(T1.name == "some name 1")))
            # 新建表和新增数据
            # async with pipeline.engine.begin() as conn:
            #     await conn.run_sync(Base.metadata.drop_all)
            #     await conn.run_sync(Base.metadata.create_all)
            #     await conn.execute(
            #         insert(T1).values(
            #             [{"name": "some name 1"}, {"name": "some name 2"}]
            #         )
            #     )

            @Control(task_name="Sqlalchemy Demo")
            async def run():
                for _ in range(100):
                    yield Request(
                        function=pipeline.find_one,
                        function_args=(select(T1).where(T1.name == "some name 1"),),
                        callback=echo,
                    )

            async def echo(request, response):
                (item,) = response
                logger.info(item.name)
                # for _ in range(10):
                #     yield Item(
                #         manager=pipeline, data={"name": "just test1"}, model_cls=T1
                #     )

            await run()

    asyncio.run(wrap())


if __name__ == "__main__":
    main()
