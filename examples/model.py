from sqlalchemy import Column, String, Integer

from aiodog import Base


class T1(Base):
    __tablename__ = "t1"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
