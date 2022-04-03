from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

engine = create_engine("sqlite:///database.db")
Base = declarative_base()
session = Session(bind=engine)
