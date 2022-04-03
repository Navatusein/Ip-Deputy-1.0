from tgbot.services.database.db import Base, engine

from tgbot.models.student import Student
from tgbot.models.subject import Subject
from tgbot.models.subject_type import SubjectType
from tgbot.models.user import User
from tgbot.models.submission import Submission
from tgbot.models.day import Day
from tgbot.models.couple import Couple
from tgbot.models.timetable import Timetable
from tgbot.models.timetable_date import TimetableDate
from tgbot.models.teacher import Teacher


def create_tables():
    Base.metadata.create_all(engine)
