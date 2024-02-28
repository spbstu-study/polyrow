from telegram import Update, Message
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

from tgbot.handlers.commands import cancel
from tgbot.states import AdminStates
from tgbot.database import DBUser


async def mailing(update: Update, _):
    message: Message = update.message
    telegram_id: int = update.message.from_user.id
    user = DBUser.get_user(telegram_id)
    
    if not user.is_admin:
        await message.reply_text('Эта фунция для вас недоступна.\nВы не являетесь администратором.')
        
        return ConversationHandler.END
        
    await message.reply_text('Введите текст рассылки:\n(Команда /cancel для отмены)')
    
    return AdminStates.TYPING_MAILING_TEXT


async def receive_mailing_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message
    user_list = DBUser.get_users()
    
    for user in user_list:
        if user.is_admin:
            continue

        try:
            await context.bot.send_message(chat_id=user.telegram_id, text=message.text)
        except TelegramError:
            continue

    await message.reply_text('Рассылка завершена.')
    
    return ConversationHandler.END


mailing_handler = ConversationHandler(
    entry_points=[CommandHandler('mailing', mailing)],
    states={
        AdminStates.TYPING_MAILING_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_mailing_text)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
