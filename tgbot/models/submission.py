from sqlalchemy import Integer, Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from tgbot.services.database.db import Base


class Submission(Base):
    __tablename__ = "Submissions"
    Id = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
    TypeId = Column(Integer(), ForeignKey('SubjectTypes.Id'), nullable=False)
    SubjectId = Column(Integer(), ForeignKey('Subjects.Id'), nullable=False)
    UserId = Column(Integer(), ForeignKey('Users.Id'), nullable=False)
    WorkNumber = Column(Integer(), nullable=False)

    User = relationship('User', back_populates='Submissions')
    Subject = relationship('Subject', uselist=False)
    SubjectType = relationship('SubjectType', uselist=False)

    def __repr__(self):
        return f"{self.Subject.get_name} {self.SubjectType.TypeName} {self.WorkNumber}"
