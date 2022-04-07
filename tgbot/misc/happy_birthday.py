import logging
import random
from datetime import datetime

from aiogram import Dispatcher
from sqlalchemy.orm import Session

from tgbot.models.student import Student

happy_birthday_list = [
    "Бажаю, щоб ОГО-ГО!"
    "\nІ ніколи не ОХО-ХО!"
    "\nТрохи АХ! Ну, можна УХ!"
    "\nЩоб захоплювало дух."
    "\nЗвичайно, щоб було ВАУ!"
    "\nІ щоб ФУ вже зовсім мало."
    "\nЗ Днем народження вітаю,"
    "\nІ за тебе випиваю!",

    "Вітаю з днем старіння ... Ой, тобто з днем народження. "
    "Нехай кістки не ломить, нехай пісок не сиплеться з тебе, нехай і "
    "раніше радують веселі анекдоти, літає високо душа. "
    "Нехай зуби не болять від смачного торта, а всі свічки на ньому задуются з першої спроби! "
    "Нехай тішать пристрасні гарячі ночі і шалено щасливі дні!",

    "Вітаю з днем варення і хочу від душі побажати, щоб завжди були повні штани радості, повні кишені зелені, "
    "повний холодильник делікатесів, повна хата щастя, повний порядок в справах і повний кайф в житті!"
]


async def birthday_check(dp: Dispatcher):
    session: Session = dp.bot.get('session')
    logger: logging.Logger = dp.bot.get('logger')

    student_list = session.query(Student).filter(Student.LastCongratulations != datetime.now().date()).all()

    someone_congratulated = False

    for student in student_list:
        user = student.User

        if user is None:
            continue

        birthday = student.birthday

        if birthday.month == datetime.now().month and birthday.day == datetime.now().day:
            logger.info(f'{user.Student} was congratulated.')

            await dp.bot.send_message(chat_id=user.TelegramId,
                                      text=happy_birthday_list[random.randint(0, len(happy_birthday_list))])
            student.LastCongratulations = datetime.now().date()

            session.flush()

            someone_congratulated = True

    if someone_congratulated:
        session.commit()

    logger.info('Birthday check complete.')

