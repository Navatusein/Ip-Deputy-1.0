from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.middlewares.localization import i18n

_ = i18n.lazy_gettext


login_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(_('🔐 Авторизоваться'), request_contact=True)
        ]
    ],
    resize_keyboard=True
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(_('🗓 Расписание')), KeyboardButton(_('🧾 Сдача'))
        ],
        [
            KeyboardButton(_('⁉ FAQ')), KeyboardButton(_('🗒 Информация'))
        ],
        [
            KeyboardButton(_('⚙ Настройки'))
        ]
    ],
    resize_keyboard=True
)

main_menu_admin = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(_('🗓 Расписание')), KeyboardButton(_('🧾 Сдача'))
        ],
        [
            KeyboardButton(_('⁉ FAQ')), KeyboardButton(_('🗒 Информация'))
        ],
        [
            KeyboardButton(_('⚙ Настройки'))
        ],
        [
            KeyboardButton(_('👑 Админка'))
        ]

    ],
    resize_keyboard=True
)

confirmation_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(_('↩ Назад'))
        ],
        [
            KeyboardButton(_('❎ Отменить')), KeyboardButton(_('✅ Подтвердить'))
        ]
    ],
    resize_keyboard=True
)

submission_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(_('📋 Главное меню'))
        ],
        [
            KeyboardButton(_('➕ Записаться')), KeyboardButton(_('🧾 Мои записи'))
        ],
        [
            KeyboardButton(_('🗳 Получить список'))
        ]
    ],
    resize_keyboard=True
)

submission_control_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(_('↩ Назад'))
        ],
        [
            KeyboardButton(_('❌ Снять заявку'))
        ]
    ],
    resize_keyboard=True
)

submissions_control_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(_('↩ Назад'))
        ],
        [
            KeyboardButton(_('❌ Очистить список'))
        ]
    ],
    resize_keyboard=True
)

timetable_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(_('📋 Главное меню'))
        ],
        [
            KeyboardButton(_('🕐 На сегодня')), KeyboardButton(_('🕑 На завтра'))
        ],
        [
            KeyboardButton(_('🕒 На эту неделю')), KeyboardButton(_('🕓 На следующею неделю'))
        ],
        [
            KeyboardButton(_('🗓 Всё'))
        ]
    ],
    resize_keyboard=True
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(_('📋 Главное меню'))
        ],
        [
            KeyboardButton(_('📥 Расписание')), KeyboardButton(_('📨 Уведомление'))
        ]
    ],
    resize_keyboard=True
)

information_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(_('📋 Главное меню'))
        ],
        [
            KeyboardButton(_('🧑‍🎓 Студенты')), KeyboardButton(_('🧑🏻‍🏫 Преподаватели'))
        ]
    ],
    resize_keyboard=True
)

settings_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(_('📋 Главное меню'))
        ],
        [
            KeyboardButton(_('🇷🇺 Язык'))
        ]
    ],
    resize_keyboard=True
)

language_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(_('↩ Назад'))
        ],
        [
            KeyboardButton('🇷🇺 Русский'), KeyboardButton('🇺🇦 Українська'), KeyboardButton('🇬🇧 English')
        ]
    ],
    resize_keyboard=True
)

notification_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(_('↩ Назад'))
        ],
        [
            KeyboardButton(_('🔔 Уведомление: Вкл'))
        ]
    ],
    resize_keyboard=True
)

back_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(_('↩ Назад'))
        ]
    ],
    resize_keyboard=True
)
