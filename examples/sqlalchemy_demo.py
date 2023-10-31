import asyncio
import random

from sqlalchemy import Column
from sqlalchemy import MetaData
from sqlalchemy import select
from sqlalchemy import String
from sqlalchemy import Table
from pydog import MysqlPipeline, Control, Request, Item, Base
from loguru import logger


# meta = MetaData()
# t1 = Table("t1", meta, Column("name", String(50), primary_key=True))
class T1(Base):
    __tablename__ = "t1"

    name = Column(String(50), primary_key=True, autoincrement=False)


def main():
    async def wrap():
        async with MysqlPipeline("mysql") as pipeline:

            @Control(task_name="sqlalchemy demo")
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
                        manager=pipeline,
                        data={"name": "just test"},
                        model_cls=T1
                    )

            await run()

    asyncio.run(wrap())


if __name__ == "__main__":
    main()
