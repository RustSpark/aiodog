## AIODOG
### 简介
**aiodog是基于python3.10的异步轻便执行框架，可以让你更加方便的编写异步代码。**
### 特点
- 可用于异步爬虫
    - aiohttp: https://docs.aiohttp.org/en/stable/ （已封装）
    - playwright: https://playwright.dev/python/docs/intro
- 可用于异步数据库数据处理
    - aiomysql: https://aiomysql.readthedocs.io/en/latest/ （已封装）
    - aiopg: https://aiopg.readthedocs.io/en/latest/
    - asyncpg: https://github.com/MagicStack/asyncpg
- 内部封装了[异步SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)，方便与[FastAPI](https://fastapi.tiangolo.com/zh/tutorial/sql-databases/)等web框架ORM进行集成
- 内部封装处理同步函数
- 细分业务，可以快速定位到每一步骤
- 轻便，不需要过度配置
### 环境要求
- python3.10+
### 安装
**NOTE：** 确保环境中已有poetry：https://python-poetry.org/docs/
```shell
pip install poetry
```
#### From Github
```shell
git clone https://github.com/RustSpark/aiodog.git
cd aiodog
poetry install
poetry shell
```
#### 新建.env（重新命名和修改.env.example）
```shell
cp .env.example .env # 修改里面的配置
```
#### 运行简单demo
```shell
poetry run python examples/sqlalchemy_offset_demo.py
poetry run offset
```
### 案例
1. 普通
```python
import asyncio
import random
from aiodog import Control, Request
from loguru import logger

async def test():
    sleep_time = random.uniform(1, 2)
    await asyncio.sleep(sleep_time)
    return f"Test {sleep_time}"

def main():
    async def wrap():
        @Control(task_name="Just Test")
        async def run():
            for _ in range(10):
                yield Request(
                    function=test,
                    callback=echo,
                    message=f"Run {_}"
                )
          
        async def echo(request, response):
            logger.info(response)
            
    asyncio.run(wrap())

if __name__ == "__main__":
    main()
```
2. 多个解析器
```python
import asyncio
import random
from aiodog import Parser, Control, Request
from loguru import logger

async def test1():
    sleep_time = random.uniform(1, 2)
    await asyncio.sleep(sleep_time)
    return f"Test1 {sleep_time}"

async def test2():
    sleep_time = random.uniform(1, 2)
    await asyncio.sleep(sleep_time)
    return f"Test2 {sleep_time}"

def main():
    async def wrap():
        async def run2():
            yield Request(
                function=test2,
                callback=echo2
            )
        
        async def echo2(request, response):
            logger.info(response)
            
        @Control(task_name="Test Parser")
        @Parser(callback=run2)
        async def run1():
            yield Request(
                function=test1,
                callback=echo1
            )
        
        async def echo1(request, response):
            logger.info(response)
    asyncio.run(wrap())

if __name__ == "__main__":
    main()
```
3. 多个回调
```python
import asyncio
import random
from aiodog import Control, Request
from loguru import logger

async def test():
    sleep_time = random.uniform(1, 2)
    await asyncio.sleep(sleep_time)
    return f"Test {sleep_time}"

def main():
    async def wrap():
        @Control(task_name="Test Multi Callbacks")
        async def run():
            yield Request(
                function=test,
                callback=echo
            )
        
        async def echo(request, response):
            logger.info(response)
            yield Request(
                function=test,
                callback=echo2
            )
        
        async def echo2(request, response):
            logger.info(response)
        
    asyncio.run(wrap())

if __name__ == "__main__":
    main()
```
4. Mysql跑数
```dotenv
# .env
MYSQL=mysql+aiomysql://user:password@host:port/db
# 可选，存储和来源不一致时
RESULT=mysql+aiomysql://user:password@host:port/db
```
```python
import asyncio
from functools import partial
from aiodog import Control, MysqlPipeline, Request, Item, Base, Parser
from sqlalchemy import String, Column, Integer, select
from loguru import logger


class T1(Base):
    __tablename__ = "t1"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    

def main():
    async def wrap():
        async with MysqlPipeline("mysql") as pipeline, MysqlPipeline(
          "result"
        ) as result_pipeline:
            # 另外一种写法
            async def run2():
                yield Request(
                    function=partial(pipeline.find_one, select(T1).where(T1.name == "some name 1"),),
                    callback=echo
                )
                
            @Control(task_name="Test Mysql")
            @Parser(callback=run2)
            async def run():
                yield Request(
                    function=pipeline.find_one,
                    function_args=(select(T1).where(T1.name == "some name 1"),),
                    callback=echo,
                )

            async def echo(request, response):
                item, = response
                logger.info(item)
                yield Item(
                    manager=result_pipeline,
                    model_cls=T1,
                    data={
                      "name": "Just Modify"
                    }
                )
            
            await run()
    
    asyncio.run(wrap())

if __name__ == "__main__":
    main()
```
5. session爬虫
```python
import asyncio
from functools import partial
from aiodog import ASpiderSession, Control, Request, AIOHttpResponse
from loguru import logger

def main():
    async def wrap():
        async with ASpiderSession() as session:
            @Control(task_name="Test Session Spider")
            async def run():
                yield Request(
                    function=partial(session.get, "https://www.baidu.com",),
                    callback=fetch_content,
                )
            
            async def fetch_content(request, response: AIOHttpResponse):
                logger.info(response.selector.css("title::text").getall())
            
            await run()
    asyncio.run(wrap())

if __name__ == "__main__":
    main()
```