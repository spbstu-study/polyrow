'''Предоставляет инструменты для обработки нажатия кнопок'''
import logging
from typing import Callable

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError, Forbidden

import tgbot.interface.buttons.user as user
import tgbot.interface.buttons.admin as admin
from tgbot.database import DBUser
from tgbot.getters import get_id


LOGGER = logging.getLogger()


TYPE_OF_USER_BUTTONS: dict[bool, dict[str, Callable]] = {
    False: user.TEXT_BUTTONS_PARSER,
    True: admin.TEXT_BUTTONS_PARSER,
}
CALLBACK_BUTTONS_PARSER: dict[str, Callable] = user.CALLBACK_BUTTONS_PARSER | admin.CALLBACK_BUTTONS_PARSER


async def handle_reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    user = DBUser.get_user(update.message.from_user.id)

    if user is None:
        await update.message.reply_text('Вы не зарегистрированы!\nДля регистрации введите команду /start')
        return
       
    button_function = TYPE_OF_USER_BUTTONS.get(user.is_admin).get(text) 
    if button_function is None:
        LOGGER.debug(f'Handling message from telegram user. Text "{text}" haven\'t callable function. Skip')
        return

    await button_function(update, context)


async def handle_inline_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    id = get_id(query.data)

    if id:
        query_data = query.data.replace('_' + str(id), '')
    else:
        query_data = query.data
    
    button_function = CALLBACK_BUTTONS_PARSER.get(query_data) 
    if button_function is None:
        return
    
    try:
        await button_function(update, context)
    except (TelegramError, Forbidden) as error:
        user = update.callback_query.from_user
        LOGGER.error(
            'Ошибка, возникшая при нажатии на inline button.\n'
            f'\tTG ID: {user.id}; tg.first_name и tg.last_name: {user.first_name} {user.last_name}\n'
            f'\tТекст ошибки: {error.message}'
        )
