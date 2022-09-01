import asyncio
import logging

from os import path, makedirs

from datetime import datetime

from aiogram import Bot, Dispatcher

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from sqlalchemy.orm import Session

from tgbot.config import load_config
from tgbot.misc.happy_birthday import birthday_check

from tgbot.models.student import Student

from tgbot.misc.wait_until import wait_until

from tgbot.services.database.db import create_connection
from tgbot.services.database.create import create_tables

from tgbot.middlewares.localization import i18n
from tgbot.middlewares.last_activity import LastActivity

from tgbot.filters.admin import AdminFilter
from tgbot.filters.logined import LoginFilter

from tgbot.handlers.admin_menu import register_admin_menu
from tgbot.handlers.user import register_user
from tgbot.handlers.login_menu import register_login_menu
from tgbot.handlers.main_menu import register_main_menu
from tgbot.handlers.settings_menu import register_settings_menu
from tgbot.handlers.submission_menu import register_submission_menu
from tgbot.handlers.faq_menu import register_faq_menu
from tgbot.handlers.timetable_menu import register_timetable_menu
from tgbot.handlers.information_menu import register_information_menu
from tgbot.handlers.links_menu import register_links_menu
from tgbot.handlers.echo import register_echo

# alembic revision --autogenerate -m ''
# alembic upgrade head

# pybabel extract --input-dirs=tgbot -o locales/ip_deputy_bot.pot
# pybabel update -d locales -D ip_deputy_bot -i locales/ip_deputy_bot.pot

logger = logging.getLogger(__name__)


def register_all_middlewares(dp):
    dp.setup_middleware(i18n)
    dp.setup_middleware(LastActivity())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(LoginFilter)


def register_all_handlers(dp):
    register_admin_menu(dp)
    register_user(dp)
    register_login_menu(dp)
    register_main_menu(dp)
    register_settings_menu(dp)
    register_submission_menu(dp)
    register_faq_menu(dp)
    register_timetable_menu(dp)
    register_information_menu(dp)
    register_links_menu(dp)
    register_echo(dp)


async def birthday_check_task(dp: Dispatcher):
    while True:
        await wait_until(hour=9)
        await birthday_check(dp)
        await asyncio.sleep(1)


async def main():
    log_format = u'%(levelname)s %(asctime)s [%(filename)s %(lineno)s] [%(module)s.%(funcName)s] %(message)s'

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        encoding='UTF-8'
    )

    if not path.exists('logs'):
        makedirs('logs')
    
    handler = logging.FileHandler(f'logs\log.log')
    handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(handler)

    logger.info("Starting bot.")
    config = load_config()

    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    engine, session = create_connection(config.db.connection_string)

    bot['config'] = config
    bot['session'] = session
    bot['logger'] = logger

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    create_tables(engine)

    # start
    try:
        loop = asyncio.get_event_loop()

        loop.create_task(birthday_check(dp))
        loop.create_task(birthday_check_task(dp))

        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Bot stopped!")
