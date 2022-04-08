import logging

from datetime import datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from sqlalchemy.orm import Session

from tgbot.keyboards.reply import information_menu

from tgbot.misc.states import StateStudentsInformation, StateTeachersInformation, StateSubjectsInformation

from tgbot.models.student import Student
from tgbot.models.subject import Subject
from tgbot.models.teacher import Teacher

from tgbot.middlewares.localization import i18n
from tgbot.models.user import User

_ = i18n.lazy_gettext


async def show_student_list(message: types.Message):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    student_list = session.query(Student).order_by(Student.Number).all()

    menu = [[KeyboardButton(_('↩ Назад'))]]

    for student in student_list:
        menu.append([KeyboardButton(f'{student.full_name}')])

    await message.answer(text=message.text, reply_markup=ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True))

    await StateStudentsInformation.SelectStudent.set()


async def show_student_information(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    student_name_list = message.text.split(' ')

    if len(student_name_list) != 2:
        await message.answer(text=_('Некорректный ввод!'))
        return

    student = session.query(Student).filter(Student.Lastname == student_name_list[0],
                                            Student.Firstname == student_name_list[1]).first()

    if student is None:
        await message.answer(text=_('Некорректный ввод!'))
        return

    await message.answer(text=_('{full_name}\nEmail: <code>{email}</code>\nТелефон: <code>+{phone_number}</code>'
                                '\nДень рождения: {birthday} \nТелеграм: {telegram}') .format(full_name=student.full_name,
                                                                                              email=student.Email,
                                                                                              phone_number=student.PhoneNumber,
                                                                                              birthday=student.formatted_birthday,
                                                                                              telegram=student.TelegramName))
    user_id = message.from_user.id

    # await message.bot.send_contact(chat_id=user_id, phone_number=f'+{student.PhoneNumber}', first_name=student.Firstname,
    #                               last_name=student.Lastname)


async def show_teacher_list(message: types.Message):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    teacher_list = session.query(Teacher).order_by(Teacher.Lastname).all()

    menu = [[KeyboardButton(_('↩ Назад'))]]

    for teacher in teacher_list:
        menu.append([KeyboardButton(f'{teacher.full_name}')])

    await message.answer(text=message.text, reply_markup=ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True))

    await StateTeachersInformation.SelectTeacher.set()


async def show_teacher_information(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    teacher_name_list = message.text.split(' ')

    if len(teacher_name_list) != 3:
        await message.answer(text=_('Некорректный ввод!'))
        return

    teacher = session.query(Teacher).filter(Teacher.Lastname == teacher_name_list[0],
                                            Teacher.Firstname == teacher_name_list[1],
                                            Teacher.Surname == teacher_name_list[2]).first()

    if teacher is None:
        await message.answer(text=_('Некорректный ввод!'))
        return

    await message.answer(text=_('{full_name}\nТелефон: <code>+{phone_number}</code>''\nТелеграм: {telegram}').format(
        full_name=teacher.full_name,
        phone_number=teacher.PhoneNumber,
        telegram=teacher.TelegramName))


async def show_subject_list(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    subject_list = session.query(Subject).all()

    menu = [[KeyboardButton(_('↩ Назад'))]]

    for subject in subject_list:
        menu.append([KeyboardButton(f'{subject.SubjectName}')])

    await message.answer(text=message.text, reply_markup=ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True))

    await StateSubjectsInformation.SelectSubject.set()


async def show_subject_information(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    subject_name = message.text

    subject: Subject = session.query(Subject).filter(Subject.SubjectName == subject_name).first()
    user: User = session.query(User).filter(User.TelegramId == message.from_user.id).first()

    if subject is None:
        await message.answer(text=_('Некорректный ввод!'))
        return

    timetable_list = subject.Timetables

    laboratory_set = set()
    practice_set = set()
    lectures_set = set()

    for timetable in timetable_list:
        if user.Student.Subgroup == timetable.Subgroup or timetable.Subgroup is None:
            timetable_date_list = timetable.TimetableDates

            match timetable.TypeId:
                case 1:
                    for timetable_date in timetable_date_list:
                        date = timetable_date.datetime
                        if date > datetime.now():
                            laboratory_set.add(date)
                case 2:
                    for timetable_date in timetable_date_list:
                        date = timetable_date.datetime
                        if date > datetime.now():
                            practice_set.add(date)
                case 3:
                    for timetable_date in timetable_date_list:
                        date = timetable_date.datetime
                        if date > datetime.now():
                            lectures_set.add(date)

    text_list = [f'{subject.SubjectName}\n',
                 str(_('Лабораторных дней осталось: {value}').format(value=len(laboratory_set))),
                 str(_('Практических дней осталось: {value}').format(value=len(practice_set))),
                 str(_('Лекционных дней осталось: {value}\n').format(value=len(lectures_set))),
                 str(_('Лабораторных работ: {value}').format(value=subject.LaboratoryCount)),
                 str(_('Практических работ: {value}').format(value=subject.PracticalCount))]

    await message.answer(text='\n'.join(text_list))


async def back_to_information_menu(message: types.Message, state: FSMContext):
    await message.answer(text=message.text, reply_markup=information_menu)
    await state.finish()


def register_information_menu(dp: Dispatcher):
    dp.register_message_handler(back_to_information_menu, text=_('↩ Назад'), state=[
        StateTeachersInformation.SelectTeacher,
        StateStudentsInformation.SelectStudent,
        StateSubjectsInformation.SelectSubject])

    dp.register_message_handler(show_teacher_list, text=_('🧑🏻‍🏫 Преподаватели'), is_logined=True)
    dp.register_message_handler(show_teacher_information, state=StateTeachersInformation.SelectTeacher)

    dp.register_message_handler(show_student_list, text=_('🧑‍🎓 Студенты'), is_logined=True)
    dp.register_message_handler(show_student_information, state=StateStudentsInformation.SelectStudent)

    dp.register_message_handler(show_subject_list, text=_('📖 Предметы'), is_logined=True)
    dp.register_message_handler(show_subject_information, state=StateSubjectsInformation.SelectSubject)

