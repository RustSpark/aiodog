from sqlalchemy.dialects.mysql import insert

from ...db.async_sqlalchemy import Pipeline


class MysqlPipeline(Pipeline):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    async def add_batch(self, table, table_value) -> str:
        stmt = insert(table).values(data := table_value["data"])
        update_cols = table_value["update_cols"] or data[0].keys()
        upsert_stmt = stmt.on_duplicate_key_update(
            {
                **{
                    name: inserted
                    for inserted in stmt.inserted
                    if (name := inserted.name) in update_cols
                }
            }
        )
        await self.transaction(upsert_stmt)
        return f"`Table:{table.__tablename__}` Upsert Success!"
