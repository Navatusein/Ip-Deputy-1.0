from datetime import datetime

from sqlalchemy import Integer, Column, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship

from tgbot.services.database.db import Base


class Faq(Base):
    __tablename__ = "Faq"
    Id = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
    FaqName = Column(String(250), unique=True, nullable=False)
    UserId = Column(Integer(), ForeignKey('User.Id'), nullable=False)
    ChapterId = Column(Integer(), ForeignKey('FaqChapters.Id'), nullable=False)
    DateCreation = Column(Date, nullable=False, default=datetime.now())
