from sqlalchemy import Integer, Column, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from tgbot.services.database.db import Base


class Day(Base):
    __tablename__ = "Days"
    Id = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
    Day = Column(String(25), unique=True, nullable=False)

    Timetables = relationship('Timetable', back_populates='Day')
