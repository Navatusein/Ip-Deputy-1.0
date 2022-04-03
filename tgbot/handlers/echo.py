from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hcode

from tgbot.middlewares.localization import i18n

_ = i18n.gettext


async def bot_echo(message: types.Message):
    text = [
        "Эхо без состояния.",
        "Сообщение:",
        hcode(message.text)
    ]

    await message.answer(text='\n'.join(text))


async def bot_echo_all(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    text = [
        f'Эхо в состоянии {hcode(state_name)}',
        'Содержание сообщения:',
        hcode(message.text)
    ]
    await message.answer(text='\n'.join(text))


def register_echo(dp: Dispatcher):
    dp.register_message_handler(bot_echo, is_logined=True)
    dp.register_message_handler(bot_echo_all, state="*", content_types=types.ContentTypes.ANY, is_logined=True)
