import sys
import traceback
from typing import Optional, Tuple, Union

from aiomysql import Cursor, DictCursor, SSCursor, SSDictCursor
from aiomysql.pool import Pool, _create_pool, _PoolContextManager
from loguru import logger

from .. import setting


class AsyncMysql(_PoolContextManager):
    def __init__(
        self,
        ip: Optional[str] = None,
        port: Optional[int] = None,
        db_name: Optional[str] = None,
        user_name: Optional[str] = None,
        user_password: Optional[str] = None,
        loop=None,
        autocommit: bool = False,
    ) -> None:
        self._ip = ip or setting.MYSQL_IP
        self._port = port or setting.MYSQL_PORT or 3306
        self._autocommit = autocommit
        super().__init__(
            coro=_create_pool(
                host=self._ip,
                port=self._port,
                user=user_name or setting.MYSQL_USER_NAME,
                password=user_password or setting.MYSQL_USER_PASSWORD,
                db=db_name or setting.MYSQL_DB_NAME,
                autocommit=self._autocommit,
                loop=loop,
            )
        )

    async def __aenter__(self):
        try:
            self._obj: Pool = await self._coro
        except Exception:
            logger.error(traceback.format_exc())
            sys.exit(1)
        else:
            logger.info(f"Mysql【{self._ip}:{self._port}】连接成功！")
            return self

    async def find(
        self,
        sql: str,
        args: Optional[Tuple] = None,
        cursor_class: Union[
            type[Cursor], type[SSCursor], type[DictCursor], type[SSDictCursor]
        ] = Cursor,
    ):
        try:
            async with self._obj.acquire() as connection:
                async with connection.cursor(cursor_class) as cursor:
                    await cursor.execute(sql, args)
                    return await cursor.fetchall()
        except Exception:
            logger.error(traceback.format_exc())

    async def add(self, sql: str,):
        pass
