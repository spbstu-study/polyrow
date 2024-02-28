from telegram import Update, Message
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from tgbot.database.api.user import DBUser
from tgbot.handlers.commands import cancel
from tgbot.interface.buttons.admin import on_click_change_password
from tgbot.states import AdminStates
from tgbot.json import json_change_admin_password
from tgbot.senders import send_message_to_admins


async def receive_new_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message 

    error = json_change_admin_password(message.text.strip()) 
    
    if error:
        await message.reply_text(f'Попытка установить введённый пароль не удалась. Текст ошибки:\n{error}')

        return ConversationHandler.END
    
    await message.reply_text('Пароль успешно изменён!')

    telegram_id = message.from_user.id
    user = DBUser.get_user(telegram_id)

    await send_message_to_admins(
        message=(
            f'Администратор {user.last_name} {user.first_name} установил новый пароль!\n'
            f'Новый пароль: {message.text}'
        ),
        context=context,
    )

    return ConversationHandler.END


change_password_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(on_click_change_password, 'menu_admin_change_password')],
    states={
        AdminStates.TYPING_NEW_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_password)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
