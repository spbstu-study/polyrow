'''Содержит функции для вывода меню для пользователя и администратора'''
from telegram import Update
from telegram.ext import ContextTypes

from tgbot.interface.keyboards import AdminKeyboard, UserKeyboard


async def start_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id=None):
    reply_markup = UserKeyboard.MENU

    if chat_id is None:
        chat_id = update.effective_chat.id 

    await context.bot.send_message( 
        chat_id=chat_id, 
        text='Все, что может бот, у тебя во встроенной клавиатуре!\nОписание функций будет добавлено позже!',
        reply_markup=reply_markup,
    )


async def start_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id=None):
    reply_markup = AdminKeyboard.MENU

    if chat_id is None:
        chat_id = update.effective_chat.id 

    await context.bot.send_message( 
        chat_id=chat_id, 
        text='Все, что может бот, у тебя во встроенной клавиатуре!\nОписание функций будет добавлено позже!',
        reply_markup=reply_markup,
    )
