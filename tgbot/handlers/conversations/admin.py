from telegram import Update, Message
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters,  ContextTypes

from tgbot.handlers.commands import cancel
from tgbot.states import AdminStates
from tgbot.json import get_password
from tgbot.database import DBUser
from tgbot.interface.menu import start_admin_menu
from tgbot.senders import send_message_to_admins


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id: int = update.message.from_user.id 

    user = DBUser.get_user(telegram_id)

    if user is None:
        await update.message.reply_text('Вы ещё не зарегистрированы!\nДля регистрации напишите /start') 

        return ConversationHandler.END
    
    if not user.is_admin: 
        await update.message.reply_text('Введите пароль администратора, чтобы продолжить.\nКоманда отмены: /cancel') 

        return AdminStates.TYPING_PASSWORD
    else:
        await start_admin_menu(update, context)


async def receive_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message 
    password = get_password()

    if message.text.strip() != password: 
        await message.reply_text('Неверный пароль!\nВведите пароль снова или введите команду отмены /cancel.')

        return AdminStates.TYPING_PASSWORD
    
    await message.reply_text('Вход выполнен успешно!')

    await message.reply_text(
        'Не забудьте активировать уведомления пользователям и администраторам командой /setjobs\n'
        'Её необходимо вводить при каждом перезапуске бота.'
    )

    telegram_id = message.from_user.id
    user = DBUser.get_user(telegram_id)

    await send_message_to_admins(
        message=(f'Авторизовался новый администратор: {user.last_name} {user.first_name}'),
        context=context,
    )
    
    DBUser.set_admin(telegram_id, set=True) 
    await start_admin_menu(update, context)

    return ConversationHandler.END


admin_handler = ConversationHandler(
    entry_points=[CommandHandler('admin', admin)],
    states={
        AdminStates.TYPING_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_password)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
