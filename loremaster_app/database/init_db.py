from .table_declarations import Base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pathlib import Path

import sqlalchemy
import sqlalchemy.orm
import os

engine:sqlalchemy.engine.base.Engine = None

db_name = 'loremaster.db'

def db_file_present(instance_path:str):
    return os.path.exists(os.path.join(instance_path, db_name))

def create_db_file(instance_path:str):
    try:
        os.makedirs(os.path.join(instance_path))
    except:
        pass
    with open(os.path.join(instance_path, db_name), 'w') as file:
        file.close();

def create_db(instance_path:str):
    create_db_file(instance_path)
    set_engine(instance_path)
    create_tables(engine)

def set_engine(instance_path:str):
    global engine
    engine = create_engine('sqlite:///'+os.path.join(instance_path, db_name))

def create_tables(engine:sqlalchemy.engine.base.Engine):
    Base.metadata.create_all(bind=engine)

def create_session(engine:sqlalchemy.engine.base.Engine):
    return sessionmaker(bind=engine,
                        future = True)

def init_db(instance_path:str) -> sessionmaker:
    if not db_file_present(instance_path):
        create_db(instance_path)
    else:
        set_engine(instance_path)

    create_image_folder(instance_path=instance_path)

    return create_session(engine)

def get_sessionmaker(instance_path:str) -> sessionmaker:
    if db_file_present(instance_path):
        set_engine(instance_path)

        return create_session(engine)
    return None

def create_image_folder(instance_path:str) -> None:
    if not os.path.exists(os.path.join(instance_path, 'images')):
        os.makedirs(os.path.join(instance_path, 'images'))

Session = init_db((Path(__file__) / "../../instance").resolve())
