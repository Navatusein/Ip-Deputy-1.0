from sqlalchemy import Integer, Column, String, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from tgbot.services.database.db import Base


class Subject(Base):
    __tablename__ = "Subjects"
    Id = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
    SubjectName = Column(String(100), unique=True, nullable=False)
    SubjectShortName = Column(String(50), unique=True, nullable=True)
    LaboratoryCount = Column(Integer(), nullable=False, default=0)
    NeedLaboratorySubmission = Column(Boolean(), default=False)
    PracticalCount = Column(Integer(), nullable=False, default=0)
    NeedPracticalSubmission = Column(Boolean(), default=False)

    Submissions = relationship('Submission', back_populates='Subject')
    Timetables = relationship('Timetable', back_populates='Subject')

    @hybrid_property
    def get_name(self):
        if self.SubjectShortName is not None:
            return self.SubjectShortName
        else:
            return self.SubjectName

    def __repr__(self):
        return str(self.Id)
