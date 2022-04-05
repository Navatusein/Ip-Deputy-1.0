import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from sqlalchemy.orm import Session

from tgbot.models.user import User
from tgbot.models.student import Student

from tgbot.misc.states import StateLogin

from tgbot.keyboards.reply import main_menu

from tgbot.middlewares.localization import i18n

_ = i18n.lazy_gettext


async def login_contact(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    user_id = message.from_user.id
    phone_number = message.contact['phone_number']
    student: Student = session.query(Student).filter(Student.PhoneNumber == str(int(phone_number))).first()

    if message.contact['user_id'] != user_id:
        await message.answer(_('Это не ваш контакт!'))
        logger.warning(f"id: {user_id} user: {message.from_user.username} sent the wrong contact.")
        return

    if student is None:
        await message.answer(_('Вас нету в базе данных!'))
        logger.warning(f"id: {user_id} phone: {phone_number} user: {message.from_user.username} can't be find in the database.")
        return

    user: User = User(TelegramId=user_id, StudentId=student.Id, Language='uk')
    session.add(user)
    session.commit()

    await message.answer(_('Авторизация прошла успешно!'), reply_markup=main_menu)
    logger.info(f"id: {user_id} phone: {phone_number} user: {message.from_user.username} added to users table successfully.")
    await state.finish()


async def login(message: types.Message):
    await message.answer(_('Нажмите на кнопку авторизоваться!'))


def register_login_menu(dp: Dispatcher):
    dp.register_message_handler(login_contact, content_types=['contact'], state=StateLogin.Login)
    dp.register_message_handler(login, state=StateLogin.Login)
