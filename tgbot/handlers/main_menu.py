import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy.orm import Session

from tgbot.keyboards.reply import main_menu, main_menu_admin, submission_menu, timetable_menu, admin_menu, \
    information_menu, settings_menu

from tgbot.middlewares.localization import i18n
from tgbot.misc.states import StateLinksMenu
from tgbot.models.links import Link
from tgbot.models.links_tabs import LinkTab

_ = i18n.lazy_gettext


async def show_main_menu(message: types.Message, state: FSMContext):
    await message.answer(text=message.text, reply_markup=main_menu)
    await state.finish()


async def show_main_menu_admins(message: types.Message, state: FSMContext):
    await message.answer(text=message.text, reply_markup=main_menu_admin)
    await state.finish()


async def show_submission_menu(message: types.Message):
    await message.answer(text=message.text, reply_markup=submission_menu)


async def show_timetable_menu(message: types.Message):
    await message.answer(text=message.text, reply_markup=timetable_menu)


async def show_settings_menu(message: types.Message):
    await message.answer(text=message.text, reply_markup=settings_menu)


async def show_faq_menu(message: types.Message):
    await message.answer(text=_('Бодя лентяй ещё не сделал 🤪'))


async def show_information_menu(message: types.Message):
    await message.answer(text=message.text, reply_markup=information_menu)


async def show_links_menu(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    link_tab_list = session.query(LinkTab).where(LinkTab.Path == '/').all()
    link_list = session.query(Link).where(Link.Path == '/').all()

    menu = [[KeyboardButton(_('📋 Главное меню'))]]

    for link_tab in link_tab_list:
        menu.append([KeyboardButton(f'📂 {link_tab.Name}')])

    for link in link_list:
        menu.append([KeyboardButton(f'🌐 {link.Name}')])

    await StateLinksMenu.Active.set()

    async with state.proxy() as data:
        data['position'] = '/'

    await message.answer(text=message.text, reply_markup=ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True))


async def show_admin_menu(message: types.Message):
    await message.answer(text=message.text, reply_markup=admin_menu)


async def show_admin_menu_non_admin(message: types.Message):
    await message.answer(text=_('Недостаточно прав!'))


def register_main_menu(dp: Dispatcher):
    dp.register_message_handler(show_main_menu_admins, text=_('📋 Главное меню'), state='*', is_admin=True)
    dp.register_message_handler(show_main_menu, text=_('📋 Главное меню'), state='*', is_logined=True)

    dp.register_message_handler(show_main_menu_admins, text=_('↩ Назад'), is_admin=True)
    dp.register_message_handler(show_main_menu, text=_('↩ Назад'), is_logined=True)

    dp.register_message_handler(show_submission_menu, text=_('🧾 Сдача'), is_logined=True)
    dp.register_message_handler(show_timetable_menu, text=_('🗓 Расписание'), is_logined=True)
    dp.register_message_handler(show_settings_menu, text=_('⚙ Настройки'), is_logined=True)
    dp.register_message_handler(show_links_menu, text=_('🌐 Ссылки'), is_logined=True)
    dp.register_message_handler(show_faq_menu, text=_('⁉ FAQ'), is_logined=True)
    dp.register_message_handler(show_information_menu, text=_('🗒 Информация'), is_logined=True)

    dp.register_message_handler(show_admin_menu, text=_('👑 Админка'), is_admin=True)
    dp.register_message_handler(show_admin_menu_non_admin, text=_('👑 Админка'))
