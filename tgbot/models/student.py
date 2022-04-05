from datetime import datetime

from sqlalchemy import Integer, Column, String, Date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from tgbot.services.database.db import Base


class Student(Base):
    __tablename__ = "Students"
    Id = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
    Number = Column(Integer(), unique=True, nullable=False)
    Lastname = Column(String(100), nullable=False)
    Firstname = Column(String(100), nullable=False)
    Surname = Column(String(100), nullable=False)
    PhoneNumber = Column(String(13), unique=True, nullable=False)
    Email = Column(String(100), unique=True, nullable=False)
    TelegramName = Column(String(100), unique=True)
    Birthday = Column(Date(), nullable=False)
    Subgroup = Column(Integer(), nullable=False)

    User = relationship('User', back_populates="Student", uselist=False)

    @hybrid_property
    def full_name(self):
        return f'{self.Lastname} {self.Firstname}'

    @hybrid_property
    def formatted_birthday(self):
        dt = datetime.strptime(str(self.Birthday), '%Y-%m-%d')
        return f'{dt.strftime("%d.%m.%Y")}'
