from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

Base = declarative_base()


def create_connection(connection_string: str):
    engine = create_engine(connection_string)

    session = Session(bind=engine)

    return engine, session
