from datetime import datetime

from sqlalchemy import Integer, Column, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship

from tgbot.services.database.db import Base


class FaqChapter(Base):
    __tablename__ = "FaqChapters"
    Id = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
    ChapterName = Column(String(250), unique=True, nullable=False)
