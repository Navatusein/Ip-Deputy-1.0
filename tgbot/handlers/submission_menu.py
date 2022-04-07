import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from sqlalchemy import or_

from sqlalchemy.orm import Session

from tgbot.config import Config

from tgbot.misc.states import StateRegisterSubmission
from tgbot.misc.states import StateShowSubmission
from tgbot.misc.states import StateShowSubmissionList

from tgbot.misc.emoji import circles_emoji
from tgbot.misc.emoji import number_emoji

from tgbot.models.user import User
from tgbot.models.submission import Submission
from tgbot.models.subject import Subject

from tgbot.keyboards.reply import main_menu, submissions_control_menu
from tgbot.keyboards.reply import submission_control_menu
from tgbot.keyboards.reply import submission_menu
from tgbot.keyboards.reply import confirmation_menu

from tgbot.middlewares.localization import i18n

_ = i18n.lazy_gettext


# region Register Submission
async def register_submission_begin(message: types.Message):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    subjects = session.query(Subject).filter(or_(Subject.PracticalCount != 0, Subject.LaboratoryCount != 0)).all()

    keyboard = [[KeyboardButton(_('↩ Назад'))]]

    emoji_index = 0
    for subject in subjects:
        row = []
        subject_name = subject.get_name

        if subject.NeedLaboratorySubmission:
            row.append(KeyboardButton(f"{circles_emoji[emoji_index]} {subject_name} (Лаб)"))

        if subject.NeedPracticalSubmission:
            row.append(KeyboardButton(f"{circles_emoji[emoji_index]} {subject_name} (Прак)"))

        keyboard.append(row)

        emoji_index += 1

        if emoji_index > 9:
            emoji_index = 0

    await message.answer(text=_('Выбери предмет, на сдачу которого хочешь записаться 👇'),
                         reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))

    await StateRegisterSubmission.SelectSubject.set()


async def register_submission_select_subject(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    parsed_message = message.text.split(" ")

    if len(parsed_message) < 2:
        await message.answer(text=_('Некорректный ввод!'))
        return

    subject_name = parsed_message[1]
    work_type = parsed_message[2]

    subject = session.query(Subject).filter(or_(Subject.SubjectName == subject_name,
                                                Subject.SubjectShortName == subject_name)).first()

    if subject is None:
        await message.answer(text=_('Некорректный ввод!'))
        return

    async with state.proxy() as data:
        data['subject'] = subject
        data['work_type'] = work_type

    if work_type == '(Лаб)':
        work_count = subject.LaboratoryCount
    else:
        work_count = subject.PracticalCount

    menu = [[KeyboardButton(_('↩ Назад'))]]

    row = []
    for i in range(1, work_count + 1):
        row.append(KeyboardButton(f'{i}'))

    row_size = len(row)
    if row_size >= 8:
        left = int(row_size / 2)
        right = row_size - left

        menu.append(row[:left])
        menu.append(row[right:])
    else:
        menu.append(row)

    await message.answer(text=_('Выбери номер работы 👇'),
                         reply_markup=ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True))
    await StateRegisterSubmission.SelectWorkNumber.set()


async def register_submission_select_work_number(message: types.Message, state: FSMContext):
    logger: logging.Logger = message.bot.get('logger')

    async with state.proxy() as data:
        subject = data['subject']
        work_type = data['work_type']

    if work_type == '(Лаб)':
        work_count = subject.LaboratoryCount
    else:
        work_count = subject.PracticalCount

    try:
        work_number = int(message.text)
    except ValueError:
        await message.answer(text=_('Некорректный ввод!'))
        return
    except Exception as ex:
        await message.answer(text=_('Некорректный ввод!'))
        logger.exception(ex)
        return

    if work_number not in range(1, work_count):
        await message.answer(text=_('Некорректный ввод!'))
        return

    async with state.proxy() as data:
        data['work_number'] = work_number
        subject = data['subject']
        work_type = data['work_type']

    await message.answer(text=_('{subject_name} {work_type} работа № {work_number} \nВсё правильно?')
                         .format(subject_name=subject.get_name, work_type=work_type,
                                 work_number=work_number), reply_markup=confirmation_menu)

    await StateRegisterSubmission.Confirmation.set()


async def register_submission_confirm(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    if message.text == _('❎ Отменить'):
        await message.answer(text=_('Отмена.'), reply_markup=submission_menu)
        await state.finish()
        return
    elif message.text == _('✅ Подтвердить'):
        user_id = message.from_user.id

        async with state.proxy() as data:
            subject = data['subject']
            work_type = data['work_type']
            work_number = data['work_number']

        if work_type == '(Лаб)':
            work_type_id = 1
        else:
            work_type_id = 2

        user = session.query(User).filter(User.TelegramId == user_id).first()

        for elem in user.Submissions:
            if elem.Subject.Id == subject.Id and elem.TypeId == work_type_id and elem.WorkNumber == work_number:
                await message.answer(text=_('Вы уже в списке!'), reply_markup=main_menu)
                await state.finish()
                return

        submission = Submission(TypeId=work_type_id, SubjectId=subject.Id, UserId=user.Id, WorkNumber=work_number)
        session.add(submission)
        session.commit()

        await message.answer(text=_('Вы успешно записались на сдачу 👍'), reply_markup=submission_menu)
        logger.info(f'{user} {submission} registered successfully.')
        await state.finish()
    else:
        await message.answer(text=_('Некорректный ввод!'))
        return


# endregion


# region Control Submission
async def control_submission_begin(message: types.Message):
    session: Session = message.bot.get('session')

    user_id = message.from_user.id
    user = session.query(User).filter(User.TelegramId == user_id).first()

    menu = [[KeyboardButton(_('↩ Назад'))]]

    emoji_index = 0
    for submission in user.Submissions:
        menu.append([KeyboardButton(text=f'{circles_emoji[emoji_index]} {submission}')])

        emoji_index += 1

        if emoji_index > 9:
            emoji_index = 0

    await message.answer(text=_('Ваши записи:'), reply_markup=ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True))
    await StateShowSubmission.SelectSubmission.set()


async def control_submission_select(message: types.Message, state: FSMContext):
    logger: logging.Logger = message.bot.get('logger')
    session: Session = message.bot.get('session')

    submission_str = message.text[2::]

    user_id = message.from_user.id
    user = session.query(User).filter(User.TelegramId == user_id).first()

    submissions = user.Submissions

    selected_submission = None

    for submission in submissions:
        if str(submission) == submission_str:
            selected_submission = submission
            break

    if selected_submission is None:
        await message.answer(text=_('Некорректный ввод!'))
        return

    async with state.proxy() as data:
        data['submission'] = selected_submission

    await message.answer(text=str(selected_submission), reply_markup=submission_control_menu)
    await StateShowSubmission.SelectAction.set()


async def control_submission_action(message: types.Message, state: FSMContext):
    logger: logging.Logger = message.bot.get('logger')

    if message.text == _('❌ Снять заявку'):
        async with state.proxy() as data:
            submission = data['submission']

        await message.answer(text=_('Вы уверены что хотите снять заявку? \n{submission}').format(submission=submission),
                             reply_markup=confirmation_menu)
        await StateShowSubmission.Confirmation.set()
    else:
        await message.answer(text=_('Некорректный ввод!'))
        return


async def control_submission_confirm(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    if message.text == _('❎ Отменить'):
        await message.answer(text=_('Отмена.'), reply_markup=submission_menu)
        await state.finish()
        return
    elif message.text == _('✅ Подтвердить'):
        async with state.proxy() as data:
            submission = data['submission']

        user_id = message.from_user.id
        user = session.query(User).filter(User.TelegramId == user_id).first()

        logger.info(f'{str(user)} {submission} deleted successfully.')

        session.delete(submission)
        session.commit()

        await state.finish()
        await message.answer(text=_('Заявка успешно удалена 👍'), reply_markup=submission_menu)
    else:
        await message.answer(text=_('Некорректный ввод!'))
        return


# endregion


# region Get Submissions
async def get_submissions_begin(message: types.Message):
    session: Session = message.bot.get('session')

    subjects = session.query(Subject).filter(or_(Subject.PracticalCount != 0, Subject.LaboratoryCount != 0)).all()

    menu = [[KeyboardButton(_('↩ Назад'))]]

    emoji_index = 0
    for subject in subjects:
        row = []
        subject_name = subject.get_name

        if subject.NeedLaboratorySubmission:
            row.append(KeyboardButton(f"{circles_emoji[emoji_index]} {subject_name} (Лаб)"))

        if subject.NeedPracticalSubmission:
            row.append(KeyboardButton(f"{circles_emoji[emoji_index]} {subject_name} (Прак)"))

        menu.append(row)

        emoji_index += 1

        if emoji_index > 9:
            emoji_index = 0

    await message.answer(text=_('Выбери предмет 👇'),
                         reply_markup=ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True))

    await StateShowSubmissionList.SelectSubject.set()


async def get_submissions_select_subject(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')
    config: Config = message.bot.get('config')

    parsed_message = message.text.split(" ")

    if len(parsed_message) < 2:
        await message.answer(text=_('Некорректный ввод!'))
        return

    subject_name = parsed_message[1]
    work_type = parsed_message[2]

    if work_type == '(Лаб)':
        work_type_id = 1
    else:
        work_type_id = 2

    subject = session.query(Subject).filter(or_(Subject.SubjectName == subject_name,
                                                Subject.SubjectShortName == subject_name)).first()

    if subject is None:
        await message.answer(text=_('Некорректный ввод!'))
        return

    list_submissions = []

    for submission in subject.Submissions:
        if submission.TypeId == work_type_id:
            list_submissions.append(submission)

    async with state.proxy() as data:
        data['submissions'] = list_submissions

    if not list_submissions:
        await message.answer(text=_('На сдачу не кто не записался'))
        return

    users = {}
    text_array = []

    index = 0

    for submission in list_submissions:
        user = submission.User

        if user.Id in users:
            text_array[users[user.Id]] += f', {submission.WorkNumber}'
        else:
            users[user.Id] = index
            text_array.append(
                f'{submission.User.Student.full_name} {submission.SubjectType.ShortTypeName} {submission.WorkNumber}')

    text_answer = '\n'.join(text_array)

    if message.from_user.id in config.tg_bot.admin_ids:
        await message.answer(text=text_answer, reply_markup=submissions_control_menu)
        await StateShowSubmissionList.SelectAction.set()
        return

    await message.answer(text=text_answer, reply_markup=submission_menu)
    await state.finish()


async def get_submissions_action(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    if message.text == _('❌ Очистить список'):
        await message.answer(text=_('Вы уверены что хотите очистить список?'), reply_markup=confirmation_menu)
        await StateShowSubmissionList.Confirmation.set()
    else:
        await message.answer(text=_('Некорректный ввод!'))


async def get_submissions_confirm(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    if message.text == _('❎ Отменить'):
        await message.answer(text=_('Отмена.'), reply_markup=submission_menu)
        await state.finish()
        return
    elif message.text == _('✅ Подтвердить'):
        async with state.proxy() as data:
            list_submissions = data['submissions']

        user_id = message.from_user.id
        user = session.query(User).filter(User.TelegramId == user_id).first()

        submission = session.query(Submission).filter(Submission.Id == list_submissions[0].Id).first()

        logger.info(f'Admin: {user} subject: {submission.Subject.get_name} {submission.SubjectType} '
                    f'cleared the list successfully.')

        for submission in list_submissions:
            session.delete(submission)

        session.commit()

        await state.finish()
        await message.answer(text=_('Список успешно очищен 👍'), reply_markup=submission_menu)
    else:
        await message.answer(text=_('Некорректный ввод!'))
        return

# endregion


async def back_to_submission_menu(message: types.Message, state: FSMContext):
    await message.answer(text=message.text, reply_markup=submission_menu)
    await state.finish()


def register_submission_menu(dp: Dispatcher):
    dp.register_message_handler(back_to_submission_menu, text=_('↩ Назад'), state=[
        StateRegisterSubmission.SelectSubject,
        StateRegisterSubmission.SelectWorkNumber,
        StateRegisterSubmission.Confirmation,
        StateShowSubmission.SelectSubmission,
        StateShowSubmission.SelectAction,
        StateShowSubmission.Confirmation,
        StateShowSubmissionList.SelectSubject,
        StateShowSubmissionList.SelectAction,
        StateShowSubmissionList.Confirmation])

    dp.register_message_handler(register_submission_begin, text=_('➕ Записаться'), is_logined=True)
    dp.register_message_handler(register_submission_select_subject, state=StateRegisterSubmission.SelectSubject)
    dp.register_message_handler(register_submission_select_work_number, state=StateRegisterSubmission.SelectWorkNumber)
    dp.register_message_handler(register_submission_confirm, state=StateRegisterSubmission.Confirmation)

    dp.register_message_handler(control_submission_begin, text=_('🧾 Мои записи'), is_logined=True)
    dp.register_message_handler(control_submission_select, state=StateShowSubmission.SelectSubmission)
    dp.register_message_handler(control_submission_action, state=StateShowSubmission.SelectAction)
    dp.register_message_handler(control_submission_confirm, state=StateShowSubmission.Confirmation)

    dp.register_message_handler(get_submissions_begin, text=_('🗳 Получить список'), is_logined=True)
    dp.register_message_handler(get_submissions_select_subject, state=StateShowSubmissionList.SelectSubject)
    dp.register_message_handler(get_submissions_action, state=StateShowSubmissionList.SelectAction)
    dp.register_message_handler(get_submissions_confirm, state=StateShowSubmissionList.Confirmation)
