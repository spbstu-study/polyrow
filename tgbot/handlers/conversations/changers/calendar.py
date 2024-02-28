from telegram import Update, Message
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from tgbot.handlers.commands import cancel
from tgbot.interface.buttons.admin import on_click_change_calendar
from tgbot.states import AdminStates
from config import FILENAME_CALENDAR


async def receive_new_calendar(update: Update, _):
    message: Message = update.message 

    with open(FILENAME_CALENDAR, "w", encoding="utf-8") as file:
        file.write(message.text.strip()) 

    await message.reply_text('Календарь успешно изменён!')

    return ConversationHandler.END


change_calendar_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(on_click_change_calendar, 'menu_admin_calendar')],
    states={
        AdminStates.TYPING_CALENDAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_calendar)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
