from typing import Tuple, Any

from aiogram import types, Dispatcher
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from sqlalchemy.orm import Session

from tgbot.models.user import User


class Localization(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]) -> str:
        user_id = types.User.get_current().id

        session: Session = types.User.get_current().bot.get('session')

        user = session.query(User).filter(User.TelegramId == user_id).first()

        if user is None:
            *_, data = args
            language = data['locale'] = 'uk'
            return language

        *_, data = args
        language = data['locale'] = user.Language
        return language


i18n = Localization('ip-deputy-bot', 'bot\locales')
