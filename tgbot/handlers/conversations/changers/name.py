from telegram import Update, Message
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from tgbot.handlers.commands import cancel
from tgbot.interface.buttons.user import on_click_change_first_name, on_click_change_last_name
from tgbot.states import UserStates
from tgbot.database import DBUser


async def receive_last_name_settings(update: Update, _):
    message: Message = update.message 

    last_name = message.text.strip() 

    DBUser.update_user(
        telegram_id=message.from_user.id, 
        last_name=last_name
    )

    await message.reply_text(f'Фамилия изменена: {last_name}.')

    return ConversationHandler.END


async def receive_first_name_settings(update: Update, _):
    message: Message = update.message

    first_name=message.text.strip()

    DBUser.update_user(
        telegram_id=message.from_user.id, 
        first_name=first_name
    )

    await message.reply_text(f'Имя изменено: {first_name}.')

    return ConversationHandler.END


change_first_name_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(on_click_change_first_name, 'menu_user_first_name')],
    states={
        UserStates.TYPING_FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_first_name_settings)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)


change_last_name_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(on_click_change_last_name, 'menu_user_last_name')],
    states={
        UserStates.TYPING_LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_last_name_settings)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
