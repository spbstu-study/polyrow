from telegram import Update, Message
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from tgbot.handlers.commands import cancel
from tgbot.interface.buttons.admin import on_click_change_faq
from tgbot.states import AdminStates
from config import FILENAME_FAQ


async def receive_new_faq(update: Update, _):
    message: Message = update.message 

    with open(FILENAME_FAQ, "w", encoding="utf-8") as file:
        file.write(message.text.strip()) 

    await message.reply_text('Часто задаваемые вопросы успешно изменены!')

    return ConversationHandler.END


change_faq_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(on_click_change_faq, 'menu_admin_faq')],
    states={
        AdminStates.TYPING_FAQ: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_faq)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
