'''Предоставляет обработчики диалогов

Обработчики диалогов строятся из других обработчиков.
Для удобства расширения кода помещайте все обработчики,
связанные с обработчиком диалогов, в общий модуль.
'''
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

from tgbot.handlers.conversations.admin import admin_handler
from tgbot.handlers.conversations.auth import auth_handler

from tgbot.handlers.conversations.changers.calendar import change_calendar_handler
from tgbot.handlers.conversations.changers.days import change_days_handler
from tgbot.handlers.conversations.changers.faq import change_faq_handler
from tgbot.handlers.conversations.changers.name import change_first_name_handler, change_last_name_handler
from tgbot.handlers.conversations.changers.password import change_password_handler

from tgbot.handlers.conversations.creators.workout import add_workout_handler

from tgbot.handlers.conversations.senders.mailing import mailing_handler
from tgbot.handlers.conversations.creators.result import send_result_handler
