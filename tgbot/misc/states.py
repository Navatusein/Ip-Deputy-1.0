from aiogram.dispatcher.filters.state import State, StatesGroup


class StateLogin(StatesGroup):
    Login = State()


class StateRegisterSubmission(StatesGroup):
    SelectSubject = State()
    SelectWorkNumber = State()
    Confirmation = State()


class StateShowSubmission(StatesGroup):
    SelectSubmission = State()
    SelectAction = State()
    Confirmation = State()


class StateGetSubmission(StatesGroup):
    SelectSubject = State()


class StateGetTimetableFile(StatesGroup):
    RequestTimetableFile = State()


class StateStudentsInformation(StatesGroup):
    SelectStudent = State()


class StateTeachersInformation(StatesGroup):
    SelectTeacher = State()


class StateChangeLanguage(StatesGroup):
    SelectLanguage = State()


class StateSendNotification(StatesGroup):
    RequestNotificationMessage = State()
    Confirmation = State()