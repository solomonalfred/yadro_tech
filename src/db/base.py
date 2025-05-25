import uuid
from typing import Annotated
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


MetaStr = Annotated[str, 255]
DetailedInfoStr = Annotated[str, 2000]
ends, tab = "\n", "\t"

@as_declarative()
class Base:
    __table_args__ = {"extend_existing": True}

    type_annotation_map = {MetaStr: String(255), DetailedInfoStr: String(2000)}

    def __repr__(self):
        columns = []
        for column in self.__table__.columns.keys():
            columns.append(f"{column}={getattr(self, column)}")
        return f"[{self.__class__.__name__}]{ends}{tab}{f',{ends + tab}'.join(columns)}"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
