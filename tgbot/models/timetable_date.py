from datetime import datetime

from sqlalchemy import Integer, Column, String, DateTime, ForeignKey, Date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from tgbot.services.database.db import Base


class TimetableDate(Base):
    __tablename__ = "TimetableDates"
    Id = Column(Integer(), primary_key=True, unique=True, nullable=False)
    TimetableId = Column(Integer(), ForeignKey('Timetable.Id'))
    Date = Column(Date(), nullable=False)

    Timetable = relationship('Timetable', back_populates='TimetableDates', uselist=False)

    @hybrid_property
    def formatted_date(self):
        dt = datetime.strptime(str(self.Date), '%Y-%m-%d')
        return f'{dt.strftime("%d.%m")}'

    @hybrid_property
    def datetime(self):
        return datetime.strptime(str(self.Date), '%Y-%m-%d')

    def __repr__(self):
        return self.formatted_date
