import contextlib

MYSQL_IP = ""
MYSQL_PORT = ""
MYSQL_DB_NAME = ""
MYSQL_USER_NAME = ""
MYSQL_USER_PASSWORD = ""


with contextlib.suppress(Exception):
    from setting import *
