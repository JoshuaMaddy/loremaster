from sqlalchemy import Column, ForeignKey, Integer, String, BINARY
from sqlalchemy.orm import declarative_base, relationship
from typing import Any

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    id:int = Column(Integer, primary_key=True)
    username:str = Column(String, unique=True)
    password:bytes = Column(BINARY)

    def __init__(self, username:str, password:str, *args:Any, **kwargs:Any) -> None:
        self.username:str = username
        self.password:str = password
        
        super().__init__(*args, **kwargs)