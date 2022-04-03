import typing

from sqlalchemy.orm import Session

from aiogram.dispatcher.filters import BoundFilter

from tgbot.models.user import User


class LoginFilter(BoundFilter):
    key = 'is_logined'

    def __init__(self, is_logined: typing.Optional[bool] = None):
        self.is_logined = is_logined

    async def check(self, obj):
        if self.is_logined is None:
            return False
        session: Session = obj.bot.get('session')
        return (session.query(User).filter(User.TelegramId == obj.from_user.id).first() is not None) == self.is_logined
