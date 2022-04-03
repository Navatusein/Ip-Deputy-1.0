from sqlalchemy import Integer, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from tgbot.services.database.db import Base


class User(Base):
    __tablename__ = "Users"
    Id = Column(Integer(), primary_key=True, unique=True, nullable=False)
    TelegramId = Column(Integer(), unique=True, nullable=False)
    StudentId = Column(Integer(), ForeignKey('Students.Id'), nullable=False)
    Language = Column(String(2), nullable=False)

    Student = relationship('Student', back_populates='User', uselist=False)
    Submissions = relationship('Submission', back_populates='User')
