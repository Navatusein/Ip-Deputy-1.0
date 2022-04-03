import json
import logging

from datetime import datetime
from zipfile import ZipFile

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy.orm import Session

from tgbot.keyboards.reply import confirmation_menu, admin_menu, notification_menu, back_menu

from tgbot.misc.states import StateGetTimetableFile, StateSendNotification

from tgbot.models.subject import Subject
from tgbot.models.timetable import Timetable
from tgbot.models.timetable_date import TimetableDate
from tgbot.models.user import User

from tgbot.middlewares.localization import i18n

_ = i18n.lazy_gettext


async def timetable_file_request(message: types.Message):
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

    await message.bot.download_file_by_id(file_id=document.file_id, destination='files\\timetable\\timetable.ipd')

    subject_dict = {}

    try:
        with ZipFile('files\\timetable\\timetable.ipd') as timetable_file:
            with timetable_file.open('Subjects.json') as json_file:
                parsed_subjects_list = json.loads(json_file.read())

                session.query(Subject).delete()

                for elem in parsed_subjects_list:
                    subject = Subject(SubjectName=elem['SubjectName'], SubjectShortName=elem['SubjectShortName'],
                                      LaboratoryCount=elem['LaboratoryCount'], PracticalCount=elem['PracticalCount'])

                    session.add(subject)
                    session.flush()

                    subject_dict[subject.SubjectName] = subject.Id

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

    logger.info(f'User: {message.from_user.username} Id: {message.from_user.id} New timetable import successful')
    await message.answer(text=_('Импорт прошёл успешно!'))

    await state.finish()


async def notification_message_request(message: types.Message, state: FSMContext):
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

    await message.answer(text=_('💬 {message} \n{disable_notification_text} \n').format(message=message.text,
                                                                                       disable_notification_text=disable_notification_text),
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


async def back_to_admin_menu(message: types.Message, state: FSMContext):
    await message.answer(text=message.text, reply_markup=admin_menu)
    await state.finish()


def register_admin_menu(dp: Dispatcher):
    dp.register_message_handler(back_to_admin_menu, text=_('↩ Назад'), state=[
        StateGetTimetableFile.RequestTimetableFile,
        StateSendNotification.RequestNotificationMessage])

    dp.register_message_handler(timetable_file_request, text=_('📥 Расписание'), is_admin=True)
    dp.register_message_handler(timetable_file_get, content_types=['document', 'text'],
                                state=StateGetTimetableFile.RequestTimetableFile)

    dp.register_message_handler(notification_message_request, text=_('📨 Уведомление'), is_admin=True)
    dp.register_message_handler(notification_message_get, state=StateSendNotification.RequestNotificationMessage)
    dp.register_message_handler(notification_message_confirm, state=StateSendNotification.Confirmation)
