import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from sqlalchemy.orm import Session

from tgbot.keyboards.reply import login_menu
from tgbot.keyboards.reply import main_menu

from tgbot.models.user import User
from tgbot.models.student import Student

from tgbot.misc.states import StateLogin

from tgbot.middlewares.localization import i18n

_ = i18n.lazy_gettext


async def user_start(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    user_id = message.from_user.id
    user: User = session.query(User).filter(User.TelegramId == user_id).first()

    if user is None:
        await message.reply(text=_('Необходимо авторизоваться!'), reply_markup=login_menu)
        await StateLogin.Login.set()
    else:
        student: Student = user.Student
        await message.answer(text=_('Добро пожаловать, {firstname} {lastname}').format(firstname=student.Firstname,
                                                                                       lastname=student.Lastname),
                             reply_markup=main_menu)
        logger.info(f"id: {user_id} user: {message.from_user.username} authorized successfully.")

        await state.finish()
        

async def user_not_logined(message: types.Message):
    await message.reply(text=_('Необходимо авторизоваться!'), reply_markup=login_menu)
    await StateLogin.Login.set()


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_not_logined, is_logined=False)
    dp.register_message_handler(user_start, commands=['start'], state='*')
