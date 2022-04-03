from sqlalchemy import Integer, Column, String, Boolean
from sqlalchemy.orm import relationship

from tgbot.services.database.db import Base


class SubjectType(Base):
    __tablename__ = "SubjectTypes"
    Id = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
    TypeName = Column(String(100), unique=True, nullable=False)
    ShortTypeName = Column(String(100), unique=True, nullable=False)
