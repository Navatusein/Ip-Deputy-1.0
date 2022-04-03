from datetime import datetime

from sqlalchemy import Integer, Column, String, Date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from tgbot.services.database.db import Base


class Teacher(Base):
    __tablename__ = "Teachers"
    Id = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
    Lastname = Column(String(100), nullable=False)
    Firstname = Column(String(100), nullable=False)
    Surname = Column(String(100), nullable=False)
    PhoneNumber = Column(Integer(), unique=True)
    TelegramName = Column(String(100), unique=True)

    @hybrid_property
    def full_name(self):
        return f'{self.Lastname} {self.Firstname} {self.Surname}'
