import logging

from datetime import datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from sqlalchemy.orm import Session

from tgbot.middlewares.localization import i18n
from tgbot.misc.states import StateLinksMenu
from tgbot.models.links import Link
from tgbot.models.links_tabs import LinkTab

_ = i18n.lazy_gettext


async def links_menu_handler(message: types.Message, state: FSMContext):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')
    async with state.proxy() as data:
        position = data['position']

    parsed_message = message.text.split(' ')

    if len(parsed_message) < 2:
        await message.answer(text=_('Некорректный ввод!'))
        return

    menu = [[KeyboardButton(_('↩ Назад'))]]

    if message.text == _('↩ Назад'):
        position = '/' + '/'.join(position.split('/')[:1])

        if position == '/':
            menu = [[KeyboardButton(_('📋 Главное меню'))]]
    elif parsed_message[0] == '🌐':
        link = session.query(Link).where(Link.Name == parsed_message[1]).first()

        if link is None:
            await message.answer(text=_('Некорректный ввод!'))
            return

        menu = InlineKeyboardMarkup(row_width=1)
        menu.add(InlineKeyboardButton(text=link.Name, url=link.Url))

        text_list = [
            f'🌐 {link.Name}',
            f'{link.Description}'
        ]

        await message.answer(text='\n'.join(text_list), reply_markup=menu)
        return
    elif parsed_message[0] == '📂':
        position += parsed_message[1] + '/'
    else:
        await message.answer(text=_('Некорректный ввод!'))
        return

    link_tab_list = session.query(LinkTab).where(LinkTab.Path == position).all()
    link_list = session.query(Link).where(Link.Path == position).all()

    for link_tab in link_tab_list:
        menu.append([KeyboardButton(f'📂 {link_tab.Name}')])

    for link in link_list:
        menu.append([KeyboardButton(f'🌐 {link.Name}')])

    await StateLinksMenu.Active.set()

    async with state.proxy() as data:
        data['position'] = position

    await message.answer(text=message.text, reply_markup=ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True))


def register_links_menu(dp: Dispatcher):
    dp.register_message_handler(links_menu_handler, state=StateLinksMenu.Active)
