import asyncio
from examples.model import T1
from sqlalchemy import select, func, between
from aiodog import MysqlPipeline, Request, Control, settings
from loguru import logger


def main():
    async def wrap():
        async with MysqlPipeline("mysql") as pipeline:

            @Control(task_name="fetch max/min column data")
            async def run():
                yield Request(
                    function=pipeline.find_one,
                    function_args=(
                        select(
                            func.min(T1.id).label("min_id"),
                            func.max(T1.id).label("max_id"),
                        ),
                    ),
                    callback=fetch_offset,
                )

            async def fetch_offset(request, response):
                for start_step in range(
                    response.min_id, response.max_id, settings.fetch_step
                ):
                    if (
                        end_step := start_step + settings.fetch_step - 1
                    ) > response.max_id:
                        end_step = response.max_id

                    yield Request(
                        function=pipeline.find_all,
                        function_args=(
                            select(T1).filter(between(T1.id, start_step, end_step)),
                        ),
                        callback=fetch_step,
                    )

            async def fetch_step(request, response):
                logger.info(response)

            await run()

    asyncio.run(wrap())
