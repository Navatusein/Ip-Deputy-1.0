from sqlalchemy import Integer, Column, String, Time
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from tgbot.misc.emoji import number_emoji
from tgbot.services.database.db import Base


class Link(Base):
    __tablename__ = "Links"
    Id = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
    Path = Column(String(), nullable=False)
    Name = Column(String(), unique=True, nullable=False)
    Url = Column(String(), unique=True, nullable=False)
    Description = Column(String(), nullable=True)
