import logging
from datetime import datetime, timedelta

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from sqlalchemy.orm import Session

from tgbot.misc.emoji import number_emoji

from tgbot.models.day import Day
from tgbot.models.timetable import Timetable
from tgbot.models.timetable_date import TimetableDate

from tgbot.models.user import User

from tgbot.middlewares.localization import i18n

_ = i18n.lazy_gettext


def get_timetable_day(today: bool, message: types.Message):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    day_id = datetime.now().isoweekday()

    days_of_week = [str(_('Понедельник')), str(_('Вторник')), str(_('Среда')), str(_('Четверг')), str(_('Пятница')),
                    str(_('Суббота')), str(_('Воскресенье'))]

    text_list = []

    now = datetime.now().date()

    if today:
        text_list.append(str(_('Расписание на сегодня:')))
    else:
        text_list.append(str(_('Расписание на завтра:')))
        day_id += 1
        now += timedelta(days=1)

    day = session.query(Day).filter(Day.Id == day_id).first()

    user_id = message.from_user.id
    user = session.query(User).filter(User.TelegramId == user_id).first()
    student = user.Student

    index = 1

    timetable_list = day.Timetables

    for timetable in timetable_list:
        if timetable.Subgroup == student.Subgroup or timetable.Subgroup is None:
            timetable_dates: list[TimetableDate] = timetable.TimetableDates

            for timetable_date in timetable_dates:
                if timetable_date.Date == now:
                    text_list.append(f'{number_emoji[index]} {timetable.Couple} {timetable}')
                    index += 1
                    break

    if len(text_list) == 1:
        text_list.append(str(_("Пар нету, отдыхай 👍")))

    return '\n'.join(text_list)


def get_timetable_week(this_week: bool, message: types.Message):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    day_id = datetime.now().isoweekday()

    days_of_week = [str(_('Понедельник')), str(_('Вторник')), str(_('Среда')), str(_('Четверг')), str(_('Пятница')),
                    str(_('Суббота')), str(_('Воскресенье'))]

    text_list = []

    now = datetime.now().date()

    if this_week:
        text_list.append(str(_('Расписание на эту неделю:')))
    else:
        text_list.append(str(_('Расписание на следующую неделю:')))
        now = datetime.now().date() + timedelta(days=8-day_id)
        day_id = 1

    day_list = session.query(Day).filter(Day.Id >= day_id).all()

    user_id = message.from_user.id
    user = session.query(User).filter(User.TelegramId == user_id).first()
    student = user.Student

    for day in day_list:
        text_list.append(f'\n {days_of_week[day.Id - 1]} ({now.strftime("%d.%m.%Y")}):')

        timetable_list = day.Timetables
        index = 1

        for timetable in timetable_list:
            if timetable.Subgroup == student.Subgroup or timetable.Subgroup is None:
                timetable_dates: list[TimetableDate] = timetable.TimetableDates

                for timetable_date in timetable_dates:
                    if timetable_date.Date == now:
                        text_list.append(f'{" " * 5}{number_emoji[index]} {timetable.Couple} {timetable}')
                        index += 1
                        break

        if index == 1:
            text = _("Пар нету")
            text_list.append(f'{" " * 5}{text}')

        now += timedelta(days=1)
    return '\n'.join(text_list)


async def show_today_timetable(message: types.Message):
    await message.answer(text=get_timetable_day(True, message))


async def show_tomorrow_timetable(message: types.Message):
    await message.answer(text=get_timetable_day(False, message))


async def show_this_week_timetable(message: types.Message):
    await message.answer(text=get_timetable_week(True, message))


async def show_next_week_timetable(message: types.Message):
    await message.answer(text=get_timetable_week(False, message))


async def show_full_timetable(message: types.Message):
    session: Session = message.bot.get('session')
    logger: logging.Logger = message.bot.get('logger')

    days_of_week = [str(_('Понедельник')), str(_('Вторник')), str(_('Среда')), str(_('Четверг')), str(_('Пятница')),
                    str(_('Суббота')), str(_('Воскресенье'))]

    timetable_list = session.query(Timetable).order_by(Timetable.DayId, Timetable.CoupleId).all()

    text_list = [str(_('Расписание:'))]

    last_day_id = 0
    last_couple_id = 0

    for timetable in timetable_list:
        if last_day_id != timetable.DayId:
            text_list.append(f'\n{days_of_week[timetable.DayId - 1]}:')
            last_day_id = timetable.DayId
            last_couple_id = 0

        if last_couple_id != timetable.CoupleId:
            text = _('Пара')
            text_list.append(f'{" " * 5}{text} {timetable.Couple.Number} {timetable.Couple}')
            last_couple_id = timetable.CoupleId

        text_list.append(f'{" " * 10}{timetable} {timetable.get_subgroup} {timetable.DateString}')

    await message.answer(text='\n'.join(text_list), parse_mode='HTML')


def register_timetable_menu(dp: Dispatcher):
    dp.register_message_handler(show_today_timetable, text=_('🕐 На сегодня'), is_logined=True)
    dp.register_message_handler(show_tomorrow_timetable, text=_('🕑 На завтра'), is_logined=True)
    dp.register_message_handler(show_this_week_timetable, text=_('🕒 На эту неделю'), is_logined=True)
    dp.register_message_handler(show_next_week_timetable, text=_('🕓 На следующею неделю'), is_logined=True)
    dp.register_message_handler(show_full_timetable, text=_('🗓 Всё'), is_logined=True)
