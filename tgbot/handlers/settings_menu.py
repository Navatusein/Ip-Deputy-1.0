import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from sqlalchemy.orm import Session

from tgbot.keyboards.reply import language_menu, settings_menu

from tgbot.misc.states import StateChangeLanguage

from tgbot.models.user import User

from tgbot.middlewares.localization import i18n

_ = i18n.lazy_gettext


async def show_language_menu(message: types.Message):
    await message.answer(text=message.text, reply_markup=language_menu)
    await StateChangeLanguage.SelectLanguage.set()


async def select_language(message: types.Message, state: FSMContext):
    language_list = {'🇷🇺 Русский': 'ru', '🇷🇼 Українська': 'uk', '🇬🇧 English': 'en'}

    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    if message.text not in language_list.keys():
        await message.answer(text=_('Некорректный ввод!'))
        return

    user_id = message.from_user.id

    user = session.query(User).filter(User.TelegramId == user_id).first()

    user.Language = language_list[message.text]

    session.commit()

    i18n.ctx_locale.set(user.Language)

    await message.answer(text=message.text, reply_markup=settings_menu)
    await state.finish()


async def back_to_settings_menu(message: types.Message, state: FSMContext):
    await message.answer(text=message.text, reply_markup=settings_menu)
    await state.finish()


def register_settings_menu(dp: Dispatcher):
    dp.register_message_handler(back_to_settings_menu, text=_('↩ Назад'), state=[
        StateChangeLanguage.SelectLanguage])

    dp.register_message_handler(show_language_menu, text=_('🇷🇺 Язык'))
    dp.register_message_handler(select_language, state=StateChangeLanguage.SelectLanguage)
