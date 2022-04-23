import logging
from datetime import datetime
from typing import Tuple, Any

from aiogram import types, Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from sqlalchemy.orm import Session

from tgbot.models.user import User


class LastActivity(BaseMiddleware):
    def __int__(self):
        super(LastActivity, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        session: Session = message.bot.get('session')
        logger: logging.Logger = message.bot.get('logger')

        user_id = message.from_user.id

        user = session.query(User).where(User.TelegramId == user_id).first()

        user.Student.LastActivity = datetime.now()

        session.commit()
