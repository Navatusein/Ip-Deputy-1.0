from sqlalchemy import Integer, Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from tgbot.services.database.db import Base


class Timetable(Base):
    __tablename__ = "Timetable"
    Id = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
    TypeId = Column(Integer(), ForeignKey('SubjectTypes.Id'), nullable=False)
    SubjectId = Column(Integer(), ForeignKey('Subjects.Id', ondelete="cascade"), nullable=False)
    CoupleId = Column(Integer(), ForeignKey('Couples.Id'), nullable=False)
    DayId = Column(Integer(), ForeignKey('Days.Id'), nullable=False)
    Subgroup = Column(Integer())
    AdditionalInformation = Column(String(), nullable=True)
    DateString = Column(String(), nullable=False)

    SubjectType = relationship('SubjectType', uselist=False)
    Subject = relationship('Subject', uselist=False)
    Couple = relationship('Couple', uselist=False)
    Day = relationship('Day', uselist=False)
    TimetableDates = relationship('TimetableDate')

    @hybrid_property
    def get_subgroup(self):
        if self.Subgroup is None:
            return ''
        else:
            return f'11/{self.Subgroup}'

    def __repr__(self):
        return f'{self.Subject.get_name} ({self.SubjectType.ShortTypeName})'
