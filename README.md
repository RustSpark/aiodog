## AIODOG
### 简介
**aiodog是基于python3.10的异步轻便执行框架，可以让你更加方便的编写异步代码。**
### 特点
- 可用于异步爬虫
    - aiohttp: https://docs.aiohttp.org/en/stable/
    - playwright: https://playwright.dev/python/docs/intro
- 可用于异步数据库数据处理
    - aiomysql: https://aiomysql.readthedocs.io/en/latest/
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