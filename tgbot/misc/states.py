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


class StateShowSubmissionList(StatesGroup):
    SelectSubject = State()
    SelectAction = State()
    Confirmation = State()


class StateGetTimetableFile(StatesGroup):
    RequestTimetableFile = State()


class StateStudentsInformation(StatesGroup):
    SelectStudent = State()


class StateTeachersInformation(StatesGroup):
    SelectTeacher = State()


class StateSubjectsInformation(StatesGroup):
    SelectSubject = State()


class StateChangeLanguage(StatesGroup):
    SelectLanguage = State()


class StateSendNotification(StatesGroup):
    RequestNotificationMessage = State()
    Confirmation = State()


class StateAddAdditionalCouple(StatesGroup):
    SelectSubject = State()
    SelectSubjectType = State()
    SelectCouple = State()
    SelectDate = State()
    SelectSubgroup = State()
    RequestAdditionalInformation = State()
    Confirmation = State()


class StateRemoveCouple(StatesGroup):
    SelectDay = State()
    SelectCouple = State()
    SelectSubject = State()
    SelectDate = State()
    Confirmation = State()