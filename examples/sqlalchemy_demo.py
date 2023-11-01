import asyncio

from sqlalchemy import Column, String, Integer, select, insert
from pydog import MysqlPipeline, Control, Request, Item, Base
from loguru import logger


class T1(Base):
    __tablename__ = "t1"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))


def main():
    async def wrap():
        async with MysqlPipeline("mysql") as pipeline:
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
                for _ in range(10):
                    yield Request(
                        function=pipeline.find_one,
                        function_args=(select(T1).where(T1.name == "some name 1"),),
                        callback=echo,
                    )

            async def echo(request, response):
                item: T1 = response
                logger.info(item.name)
                for _ in range(10):
                    yield Item(
                        manager=pipeline, data={"name": "just test1"}, model_cls=T1
                    )

            await run()

    asyncio.run(wrap())


if __name__ == "__main__":
    main()
