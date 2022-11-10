from .table_declarations import *
from sqlalchemy.orm import Session as QuerySession
from sqlalchemy import select
from typing import Union, Type

def get_user(session:QuerySession, user_id:int) ->Union[User, None]:
    return session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

def get_element_by_id(session:QuerySession, element_type:Type, element_id:int) -> Union[Type, None]:
    return session.execute(select(element_type).where(element_type.id == element_id)).scalar_one_or_none()