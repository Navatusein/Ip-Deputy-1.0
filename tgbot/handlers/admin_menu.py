import json
import logging

from datetime import datetime
from operator import or_
from zipfile import ZipFile

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy.orm import Session

from tgbot.keyboards.reply import confirmation_menu, admin_menu, notification_menu, back_menu
from tgbot.misc.emoji import number_emoji

from tgbot.misc.states import StateGetTimetableFile, StateSendNotification, StateAddAdditionalCouple, StateRemoveCouple
from tgbot.models.couple import Couple
from tgbot.models.day import Day

from tgbot.models.subject import Subject
from tgbot.models.subject_type import SubjectType
from tgbot.models.timetable import Timetable
from tgbot.models.timetable_date import TimetableDate
from tgbot.models.user import User

from tgbot.middlewares.localization import i18n

_ = i18n.lazy_gettext


# region Timetable File
async def timetable_file_begin(message: types.Message):
    await message.answer(text=_("Отправьте файл с расписанием"), reply_markup=back_menu)
    await StateGetTimetableFile.RequestTimetableFile.set()


async def timetable_file_get(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    document = message.document

    if document is None:
        await message.answer(text=_('Вы не отправили файл!'))
        return

    if not document.file_name.__contains__('.ipd'):
        await message.answer(text=_('Не правильный файл!'))

    await message.bot.download_file_by_id(file_id=document.file_id, destination='files/timetable/timetable.ipd')

    subject_dict = {}

    try:
        with ZipFile('files/timetable/timetable.ipd') as timetable_file:
            with timetable_file.open('Subjects.json') as json_file:
                parsed_subjects_list = json.loads(json_file.read())

                # session.query(Subject).delete()

                new_subjects = []

                for elem in parsed_subjects_list:

                    subject: Subject = session.query(Subject).where(Subject.SubjectName == elem['SubjectName']).first()

                    if subject is not None:
                        subject.SubjectShortName = elem['SubjectShortName']
                        subject.LaboratoryCount = elem['LaboratoryCount']
                        subject.PracticalCount = elem['PracticalCount']
                        subject.NeedLaboratorySubmission = elem['NeedLaboratorySubmission']
                        subject.NeedPracticalSubmission = elem['NeedPracticalSubmission']

                    else:
                        subject = Subject(SubjectName=elem['SubjectName'], SubjectShortName=elem['SubjectShortName'],
                                          LaboratoryCount=elem['LaboratoryCount'],
                                          PracticalCount=elem['PracticalCount'],
                                          NeedLaboratorySubmission=elem['NeedLaboratorySubmission'],
                                          NeedPracticalSubmission=elem['NeedPracticalSubmission'])

                        session.add(subject)

                    new_subjects.append(subject)

                    session.flush()

                    subject_dict[subject.SubjectName] = subject.Id

                subject_list = session.query(Subject).all()

                subjects_to_delete = list(set(subject_list) - set(new_subjects))

                for elem in subjects_to_delete:
                    session.delete(elem)
                    session.flush()

            with timetable_file.open('Timetable.json') as json_file:
                parsed_timetable_list = json.loads(json_file.read())

                session.query(Timetable).delete()
                session.query(TimetableDate).delete()

                for elem in parsed_timetable_list:
                    parsed_timetable_date_list = elem['TimetableDateList']

                    timetable = Timetable(TypeId=elem['TypeId'], CoupleId=elem['CoupleId'], DayId=elem['DayId'],
                                          SubjectId=subject_dict[elem['SubjectObject']['SubjectName']],
                                          Subgroup=elem['Subgroup'],
                                          AdditionalInformation=elem['AdditionalInformation'],
                                          DateString=elem['DateString'])

                    session.add(timetable)
                    session.flush()

                    timetable_date_list = []

                    for date in parsed_timetable_date_list:
                        dt = datetime.strptime(date, '%d.%m.%Y')

                        timetable_date_list.append(TimetableDate(TimetableId=timetable.Id, Date=dt))

                    session.add_all(timetable_date_list)
                    session.flush()
            session.commit()
    except Exception as ex:
        await message.answer(text=_('Ошибка: \n {exception}').format(exception=ex))
        logger.error(f'User: {message.from_user.username} Id: {message.from_user.id} {ex}')
        return

    # noinspection PyUnresolvedReferences
    user = session.query(User).filter(User.TelegramId == message.from_user.id).first()

    logger.info(f'Admin {user} new timetable import successful.')
    await message.answer(text=_('Импорт прошёл успешно!'))

    await state.finish()


# endregion
# region Notification Message
async def notification_message_begin(message: types.Message, state: FSMContext):
    await message.answer(text=_('Напишите сообщение 👇'), reply_markup=notification_menu)
    await StateSendNotification.RequestNotificationMessage.set()

    async with state.proxy() as data:
        data['disable_notification'] = False


async def notification_message_get(message: types.Message, state: FSMContext):
    if message.text == _('🔔 Уведомление: Вкл'):
        menu = [[KeyboardButton(_('↩ Назад'))], [KeyboardButton(_('🔕 Уведомление: Выкл'))]]

        await message.answer(text=_('🔕 Уведомление: Выкл'),
                             reply_markup=ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True))

        async with state.proxy() as data:
            data['disable_notification'] = True

        return
    elif message.text == _('🔕 Уведомление: Выкл'):
        menu = [[KeyboardButton(_('↩ Назад'))], [KeyboardButton(_('🔔 Уведомление: Вкл'))]]

        await message.answer(text=_('🔔 Уведомление: Вкл'),
                             reply_markup=ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True))

        async with state.proxy() as data:
            data['disable_notification'] = False

        return

    async with state.proxy() as data:
        data['message'] = message.text
        disable_notification = data['disable_notification']

    if disable_notification:
        disable_notification_text = _('🔕 Уведомление: Выкл')
    else:
        disable_notification_text = _('🔔 Уведомление: Вкл')

    await message.answer(text=_('💬 {message} \n{disable_notification_text} \n')
                         .format(message=message.text, disable_notification_text=disable_notification_text),
                         reply_markup=confirmation_menu)

    await StateSendNotification.Confirmation.set()


async def notification_message_confirm(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    if message.text == _('❎ Отменить'):
        await message.answer(text=_('Отмена'), reply_markup=admin_menu)
        await state.finish()
        return

    elif message.text == _('✅ Подтвердить'):
        user_list = session.query(User).all()

        async with state.proxy() as data:
            message_text = data['message']
            disable_notification = data['disable_notification']

        print(disable_notification)

        await message.answer(text=_('Уведомление успешно отправлено 👍'), reply_markup=admin_menu)

        for user in user_list:
            await message.bot.send_message(user.TelegramId, text=message_text,
                                           disable_notification=disable_notification,
                                           allow_sending_without_reply=disable_notification)

        logger.info(f'User: {message.from_user.username} Id: {message.from_user.id} Send notification {message_text}')

        await state.finish()
    else:
        await message.answer(text=_('Некорректный ввод!'))
        return


# endregion
# region Add Timetable
async def add_timetable_begin(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    subject_list = session.query(Subject).all()

    keyboard = [[KeyboardButton(_('↩ Назад'))]]

    for subject in subject_list:
        keyboard.append([KeyboardButton(subject.SubjectName)])

    await StateAddAdditionalCouple.SelectSubject.set()

    await message.answer(text=_('Выбери предмет 👇'),
                         reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))


async def add_timetable_select_subject(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    # noinspection PyUnresolvedReferences
    subject = session.query(Subject).filter(Subject.SubjectName == message.text).first()

    if subject is None:
        await message.answer(text=_('Некорректный ввод!'))
        return

    async with state.proxy() as data:
        data['subject_id'] = subject.Id

    subject_type_list = session.query(SubjectType).all()

    keyboard = [[KeyboardButton(_('↩ Назад'))]]

    for subject_type in subject_type_list:
        keyboard.append([KeyboardButton(subject_type.TypeName)])

    await StateAddAdditionalCouple.SelectSubjectType.set()

    await message.answer(text=_('Выбери тип занятия 👇'),
                         reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))


async def add_timetable_select_subject_type(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    # noinspection PyUnresolvedReferences
    subject_type = session.query(SubjectType).filter(SubjectType.TypeName == message.text).first()

    if subject_type is None:
        await message.answer(text=_('Некорректный ввод!'))
        return

    async with state.proxy() as data:
        data['subject_type_id'] = subject_type.Id

    keyboard = [[KeyboardButton(_('↩ Назад'))]]

    couple_list = session.query(Couple).all()

    index = 1

    for couple in couple_list:
        keyboard.append([KeyboardButton(f'{number_emoji[index]} {couple}')])
        index += 1

    await StateAddAdditionalCouple.SelectCouple.set()

    await message.answer(text=_("Выберете пару 👇"),
                         reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))


async def add_timetable_select_couple(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    parsed_message = message.text.split(" ")

    if len(parsed_message) < 2:
        await message.answer(text=_('Некорректный ввод!'))
        return

    parsed_message = parsed_message[1].split('-')

    if len(parsed_message) < 2:
        await message.answer(text=_('Некорректный ввод!'))
        return

    # noinspection PyUnresolvedReferences
    couple = session.query(Couple).filter(Couple.TimeBegin == parsed_message[0] + ':00',
                                          Couple.TimeEnd == parsed_message[1] + ':00').first()

    if couple is None:
        await message.answer(text=_('Некорректный ввод!'))
        return

    async with state.proxy() as data:
        data['couple_id'] = couple.Id

    keyboard = [[KeyboardButton(_('↩ Назад'))]]

    await StateAddAdditionalCouple.SelectDate.set()

    await message.answer(text=_("Введите дату занятия в формате дд.мм.гггг 👇"),
                         reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))


async def add_timetable_select_date(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    try:
        date = datetime.strptime(message.text, '%d.%m.%Y')
    except ValueError as ex:
        await message.answer(text=_('Некорректный ввод!'))
        return
    except Exception as ex:
        await message.answer(text=_('Некорректный ввод!'))
        logger.exception(ex)
        return

    if date < datetime.now():
        await message.answer(text=_('Ввёденная дата должна быть больше сегодняшней!'))
        return

    async with state.proxy() as data:
        data['date'] = date

    keyboard = [
        [KeyboardButton(_('↩ Назад'))],
        [KeyboardButton(_('Подгруппа 1')), KeyboardButton(_('Подгруппа 2'))],
        [KeyboardButton(_('Вся группа'))]
    ]

    await StateAddAdditionalCouple.SelectSubgroup.set()

    await message.answer(text=_("Выбери подгруппу 👇"),
                         reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))


async def add_timetable_select_subgroup(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    message_text = message.text

    subgroup = None

    if message_text == _('Подгруппа 1'):
        subgroup = 1
    elif message_text == _('Подгруппа 2'):
        subgroup = 2
    elif message_text == _('Вся группа'):
        subgroup = None
    else:
        await message.answer(text=_('Некорректный ввод!'))
        return

    async with state.proxy() as data:
        data['subgroup'] = subgroup

    keyboard = [
        [KeyboardButton(_('↩ Назад'))],
        [KeyboardButton(_('❎ Нету дополнительной информации'))]
    ]

    await StateAddAdditionalCouple.RequestAdditionalInformation.set()

    await message.answer(text=_("Введите дополнительную информацию 👇"),
                         reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))


async def add_timetable_request_additional_information(message: types.Message, state: FSMContext):
    days_of_week = [str(_('Понедельник')), str(_('Вторник')), str(_('Среда')), str(_('Четверг')), str(_('Пятница')),
                    str(_('Суббота')), str(_('Воскресенье'))]

    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    if message.text == _('❎ Нету дополнительной информации'):
        additional_information = ""
    else:
        additional_information = message.text

    await StateAddAdditionalCouple.RequestAdditionalInformation.set()

    async with state.proxy() as data:
        subject_id = data['subject_id']
        subject_type_id = data['subject_type_id']
        couple_id = data['couple_id']
        subgroup = data['subgroup']
        data['additional_information'] = additional_information
        date: datetime = data['date']
    # noinspection PyUnresolvedReferences
    subject = session.query(Subject).filter(Subject.Id == subject_id).first()

    # noinspection PyUnresolvedReferences
    subject_type = session.query(SubjectType).filter(SubjectType.Id == subject_type_id).first()

    # noinspection PyUnresolvedReferences
    couple = session.query(Couple).filter(Couple.Id == couple_id).first()

    text_list = [
        str(_('Предмет:')),
        f'{" " * 4}{subject.get_name}\n',
        str(_('Тип занятия:')),
        f'{" " * 4}{subject_type.TypeName}\n',
        str(_('Пара:')),
        f'{" " * 4}{couple.__repr__()}\n',
        str(_('Дата:')),
        f'{" " * 4}{date.strftime("%d.%m.%Y")} ({days_of_week[date.weekday()]})\n',
        str(_('Подгруппа:')),
        f'{" " * 4}{(f"11/{subgroup}", str(_("Вся группа")))[subgroup is None]}\n',
        str(_('Дополнительная информация:')),
        f'{" " * 4}{additional_information}\n',
        str(_('Всё правильно?'))
    ]

    await StateAddAdditionalCouple.Confirmation.set()

    await message.answer(text='\n'.join(text_list),
                         reply_markup=confirmation_menu)


async def add_timetable_confirmation(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    if message.text == _('❎ Отменить'):
        await message.answer(text=_('Отмена.'), reply_markup=admin_menu)
        await state.finish()
        return
    elif message.text == _('✅ Подтвердить'):
        async with state.proxy() as data:
            subject_id = data['subject_id']
            subject_type_id = data['subject_type_id']
            couple_id = data['couple_id']
            subgroup = data['subgroup']
            additional_information = data['additional_information']
            date = data['date']

        day_id = date.weekday() + 1

        timetable = session.query(Timetable).filter(Timetable.TypeId == subject_type_id,
                                                    Timetable.CoupleId == couple_id,
                                                    Timetable.SubjectId == subject_id,
                                                    Timetable.DayId == day_id,
                                                    Timetable.Subgroup == subgroup).first()

        if timetable is None:
            date_string = f'[{date.strftime("%d.%m")}]'

            timetable = Timetable(TypeId=subject_type_id, SubjectId=subject_id, CoupleId=couple_id, DayId=day_id,
                                  Subgroup=subgroup, AdditionalInformation=additional_information,
                                  DateString=date_string)
        else:
            date_string = timetable.DateString.replace("]", "")
            date_string += f', {date.strftime("%d.%m")}]'

            timetable.DateString = date_string

        session.add(timetable)
        session.flush()

        timetable_date = TimetableDate(TimetableId=timetable.Id, Date=date)

        session.add(timetable_date)
        session.commit()

        user = session.query(User).filter(User.TelegramId == message.from_user.id).first()

        await message.answer(text=_('Вы успешно добавили дополнительную пару 👍'), reply_markup=admin_menu)
        logger.info(f'Admin: {user} added timetable: {timetable} successfully.')
        await state.finish()
    else:
        await message.answer(text=_('Некорректный ввод!'))
        return


# endregion
# region Remove Timetable
async def remove_timetable_begin(message: types.Message, state: FSMContext):
    days_of_week = [str(_('Понедельник')), str(_('Вторник')), str(_('Среда')), str(_('Четверг')), str(_('Пятница')),
                    str(_('Суббота')), str(_('Воскресенье'))]

    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    keyboard = [[KeyboardButton(_('↩ Назад'))]]

    index = 1

    for day in days_of_week:
        keyboard.append([KeyboardButton(f'{number_emoji[index]} {day}')])
        index += 1

    await StateRemoveCouple.SelectDay.set()

    await message.answer(text=_("Выберете день недели 👇"),
                         reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))


async def remove_timetable_select_day(message: types.Message, state: FSMContext):
    days_of_week = [str(_('Понедельник')), str(_('Вторник')), str(_('Среда')), str(_('Четверг')), str(_('Пятница')),
                    str(_('Суббота')), str(_('Воскресенье'))]

    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    parsed_message = message.text.split(' ')

    if len(parsed_message) != 2:
        await message.answer(text=_('Некорректный ввод!'))
        return

    try:
        day_id = days_of_week.index(parsed_message[1]) + 1
    except Exception as ex:
        await message.answer(text=_('Некорректный ввод!'))
        return

    async with state.proxy() as data:
        data['day_id'] = day_id

    # noinspection PyUnresolvedReferences
    day = session.query(Day).filter(Day.Id == day_id).first()

    keyboard = [[KeyboardButton(_('↩ Назад'))]]

    index = 1

    timetable_list = day.Timetables
    timetable_list.sort(key=lambda timetable_: timetable_.CoupleId)

    couple_set = set()

    for timetable in timetable_list:
        couple_set.add(timetable.Couple)

    couple_list = list(couple_set)
    couple_list.sort(key=lambda couple_: couple_.Number)

    index = 1

    for couple in couple_list:
        keyboard.append([KeyboardButton(f'{number_emoji[index]} {couple}')])
        index += 1

    await StateRemoveCouple.SelectCouple.set()

    await message.answer(text=_("Выберете день недели 👇"),
                         reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))


async def remove_timetable_select_couple(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    parsed_message = message.text.split(" ")

    if len(parsed_message) < 2:
        await message.answer(text=_('Некорректный ввод!'))
        return

    parsed_message = parsed_message[1].split('-')

    if len(parsed_message) < 2:
        await message.answer(text=_('Некорректный ввод!'))
        return

    couple = session.query(Couple).filter(Couple.TimeBegin == parsed_message[0] + ':00',
                                          Couple.TimeEnd == parsed_message[1] + ':00').first()

    if couple is None:
        await message.answer(text=_('Некорректный ввод!'))
        return

    async with state.proxy() as data:
        day_id = data['day_id']
        data['couple_id'] = couple.Id

    timetable_list = session.query(Timetable).filter(Timetable.CoupleId == couple.Id, Timetable.DayId == day_id).all()

    keyboard = [[KeyboardButton(_('↩ Назад'))]]

    for timetable in timetable_list:
        keyboard.append([KeyboardButton(f'{timetable} \n{timetable.DateString}')])

    await StateRemoveCouple.SelectSubject.set()

    await message.answer(text=_("Выберете предмет 👇"),
                         reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))


async def remove_timetable_select_subject(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    parsed_message = message.text.split(" ")

    if len(parsed_message) < 3:
        await message.answer(text=_('Некорректный ввод!'))
        return

    subgroup = None

    if parsed_message[2].__contains__('11/'):
        try:
            subgroup_ = int(parsed_message[2][3:])
        except ValueError:
            await message.answer(text=_('Некорректный ввод!'))
            return
        except Exception as ex:
            logger.exception(ex)
            await message.answer(text=_('Некорректный ввод!'))
            return

        subgroup = subgroup_

    subject_name = parsed_message[0]
    work_type = parsed_message[1]

    work_type = work_type.removeprefix('(')
    work_type = work_type.removesuffix(')')

    subject = session.query(Subject).filter(or_(Subject.SubjectName == subject_name,
                                                Subject.SubjectShortName == subject_name)).first()

    if subject is None:
        await message.answer(text=_('Некорректный ввод!'))
        return

    subject_type = session.query(SubjectType).filter(SubjectType.ShortTypeName == work_type).first()

    if subject_type is None:
        await message.answer(text=_('Некорректный ввод!'))
        return

    async with state.proxy() as data:
        day_id = data['day_id']
        couple_id = data['couple_id']

    timetable = session.query(Timetable).filter(Timetable.TypeId == subject_type.Id, Timetable.SubjectId == subject.Id,
                                                Timetable.CoupleId == couple_id, Timetable.DayId == day_id,
                                                Timetable.Subgroup == subgroup).first()

    if timetable is None:
        await message.answer(text=_('Некорректный ввод!'))
        return

    async with state.proxy() as data:
        data['timetable_id'] = timetable.Id

    timetable_date_list = session.query(TimetableDate).filter(TimetableDate.TimetableId == timetable.Id,
                                                              TimetableDate.Date >= datetime.now().date()).all()

    keyboard = [[KeyboardButton(_('↩ Назад'))]]

    for timetable_date in timetable_date_list:
        keyboard.append([KeyboardButton(f'{timetable_date.datetime.strftime("%d.%m.%Y")}')])

    await StateRemoveCouple.SelectDate.set()

    await message.answer(text=_("Выберете дату 👇"),
                         reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))


async def remove_timetable_select_date(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    try:
        date = datetime.strptime(message.text, '%d.%m.%Y')
    except ValueError:
        await message.answer(text=_('Некорректный ввод!'))
        return
    except Exception as ex:
        await message.answer(text=_('Некорректный ввод!'))
        logger.exception(ex)
        return

    async with state.proxy() as data:
        timetable_id = data['timetable_id']

    timetable = session.query(Timetable).filter(Timetable.Id == timetable_id).first()
    timetable_date = session.query(TimetableDate).filter(TimetableDate.TimetableId == timetable_id,
                                                         TimetableDate.Date == date.date()).first()

    if timetable_date is None:
        await message.answer(text=_('Некорректный ввод!'))
        return

    async with state.proxy() as data:
        data['timetable_date_id'] = timetable_date.Id

    text_list = [
        f'{timetable} {timetable_date}',
        str(_('Всё правильно?'))
    ]

    await StateRemoveCouple.Confirmation.set()

    await message.answer(text='\n'.join(text_list), reply_markup=confirmation_menu)


async def remove_timetable_confirmation(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    if message.text == _('❎ Отменить'):
        await message.answer(text=_('Отмена.'), reply_markup=admin_menu)
        await state.finish()
        return
    elif message.text == _('✅ Подтвердить'):
        async with state.proxy() as data:
            timetable_id = data['timetable_id']
            timetable_date_id = data['timetable_date_id']

        user = session.query(User).filter(User.TelegramId == message.from_user.id).first()

        timetable = session.query(Timetable).filter(Timetable.Id == timetable_id).first()
        timetable_date = session.query(TimetableDate).filter(TimetableDate.Id == timetable_date_id).first()

        session.delete(timetable_date)

        logger.info(f'Admin: {user} removed timetable date: {timetable} [{timetable_date}] successfully.')

        session.flush()

        if len(timetable.TimetableDates) == 0:
            session.delete(timetable)
            logger.info(f'Admin: {user} removed timetable: {timetable} successfully.')

        await message.answer(text=_('Вы успешно удалили пару 👍'), reply_markup=admin_menu)
        await state.finish()

        session.commit()
    else:
        await message.answer(text=_('Некорректный ввод!'))
        return


# endregion


async def back_to_admin_menu(message: types.Message, state: FSMContext):
    await message.answer(text=message.text, reply_markup=admin_menu)
    await state.finish()


def register_admin_menu(dp: Dispatcher):
    dp.register_message_handler(back_to_admin_menu, text=_('↩ Назад'), state=[
        StateGetTimetableFile.RequestTimetableFile,
        StateSendNotification.RequestNotificationMessage,
        StateSendNotification.Confirmation,
        StateAddAdditionalCouple.SelectSubject,
        StateAddAdditionalCouple.SelectSubjectType,
        StateAddAdditionalCouple.SelectCouple,
        StateAddAdditionalCouple.SelectDate,
        StateAddAdditionalCouple.SelectSubgroup,
        StateAddAdditionalCouple.RequestAdditionalInformation,
        StateAddAdditionalCouple.Confirmation,
        StateRemoveCouple.SelectDay,
        StateRemoveCouple.SelectCouple,
        StateRemoveCouple.SelectSubject,
        StateRemoveCouple.SelectDate,
        StateRemoveCouple.Confirmation
    ])

    dp.register_message_handler(timetable_file_begin, text=_('📥 Расписание'), is_admin=True)
    dp.register_message_handler(timetable_file_get, content_types=['document', 'text'],
                                state=StateGetTimetableFile.RequestTimetableFile)

    dp.register_message_handler(notification_message_begin, text=_('📨 Уведомление'), is_admin=True)
    dp.register_message_handler(notification_message_get, state=StateSendNotification.RequestNotificationMessage)
    dp.register_message_handler(notification_message_confirm, state=StateSendNotification.Confirmation)

    dp.register_message_handler(add_timetable_begin, text=_('➕ Добавить пару'), is_admin=True)
    dp.register_message_handler(add_timetable_select_subject, state=StateAddAdditionalCouple.SelectSubject)
    dp.register_message_handler(add_timetable_select_subject_type, state=StateAddAdditionalCouple.SelectSubjectType)
    dp.register_message_handler(add_timetable_select_couple, state=StateAddAdditionalCouple.SelectCouple)
    dp.register_message_handler(add_timetable_select_date, state=StateAddAdditionalCouple.SelectDate)
    dp.register_message_handler(add_timetable_select_subgroup, state=StateAddAdditionalCouple.SelectSubgroup)
    dp.register_message_handler(add_timetable_request_additional_information,
                                state=StateAddAdditionalCouple.RequestAdditionalInformation)
    dp.register_message_handler(add_timetable_confirmation, state=StateAddAdditionalCouple.Confirmation)

    dp.register_message_handler(remove_timetable_begin, text=_('➖ Удалить пару'), is_admin=True)
    dp.register_message_handler(remove_timetable_select_day, state=StateRemoveCouple.SelectDay)
    dp.register_message_handler(remove_timetable_select_couple, state=StateRemoveCouple.SelectCouple)
    dp.register_message_handler(remove_timetable_select_subject, state=StateRemoveCouple.SelectSubject)
    dp.register_message_handler(remove_timetable_select_date, state=StateRemoveCouple.SelectDate)
    dp.register_message_handler(remove_timetable_confirmation, state=StateRemoveCouple.Confirmation)
