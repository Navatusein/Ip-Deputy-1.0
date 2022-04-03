from sqlalchemy import Integer, Column, String, Time
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from tgbot.misc.emoji import number_emoji
from tgbot.services.database.db import Base


class Couple(Base):
    __tablename__ = "Couples"
    Id = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
    Number = Column(Integer(), unique=True, nullable=False)
    TimeBegin = Column(Time(), unique=True, nullable=False)
    TimeEnd = Column(Time(), unique=True, nullable=False)

    Timetables = relationship('Timetable', back_populates='Couple')

    @hybrid_property
    def short_time_begin(self):
        return ':'.join(str(self.TimeBegin).split(':')[:-1])

    @hybrid_property
    def short_time_end(self):
        return ':'.join(str(self.TimeEnd).split(':')[:-1])

    def __repr__(self):
        return f'{self.short_time_begin}-{self.short_time_end}'
