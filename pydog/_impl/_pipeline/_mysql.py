from sqlalchemy.dialects.mysql import insert
from loguru import logger

from ...db.async_sqlalchemy import Pipeline


class MysqlPipeline(Pipeline):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    async def add_batch(self, table, table_value) -> str:
        sql = insert(table).values(table_value)
        logger.info(sql)
        await self.transaction(sql)
        return ""