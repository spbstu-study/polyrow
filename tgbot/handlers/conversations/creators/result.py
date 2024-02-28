import logging
from datetime import datetime

from telegram import Update, Message
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.error import TelegramError, Forbidden

from tgbot.handlers.commands import cancel
from tgbot.interface.buttons.user import on_click_send_result
from tgbot.states import UserStates
from config import WORKOUT_TYPES_ALIASES_RUS
from tgbot.database import DBUser, DBResult
from tgbot.interface.keyboards import AdminKeyboard


LOGGER = logging.getLogger()


async def receive_result_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message 

    result_type = message.text.strip() 

    workout_types = WORKOUT_TYPES_ALIASES_RUS.items()

    for tuple_with_type in workout_types:
        if result_type in tuple_with_type:
            context.user_data['result_type'] = tuple_with_type[0] 

            await message.reply_text('Введите результат в виде текста:')

            return UserStates.TYPING_RESULT_TEXT

    await message.reply_text('Такого типа тренировок нет. Попробуйте еще раз или введите команду отмены /cancel:')

    return UserStates.TYPING_RESULT_TYPE


async def receive_result_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message 

    context.user_data['result_text'] = message.text.strip() 

    await message.reply_text('Введите ссылку на диск с фотографией результата:')

    return UserStates.TYPING_RESULT_URL


async def receive_result_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message
    user_telegram_id = message.from_user.id

    result_type = context.user_data['result_type']
    result_text = context.user_data['result_text']
    result_url = message.text.strip()
    result_date = datetime.now()

    DBResult.create_result(
        telegram_id=user_telegram_id,
        type=result_type,
        text=result_text,
        url=result_url,
        date=result_date,
    )

    admin_list = DBUser.get_admins()

    if admin_list is None:
        await context.bot.send_message(
            chat_id=user_telegram_id,
            text='На данный момент администраторов бота нет, оповестите тренера о выполненной тренировке самостоятельно.'
        )
        return ConversationHandler.END
    
    user = DBUser.get_user(user_telegram_id)
    user_name = f'{user.first_name} {user.last_name}' 
    type_ru = WORKOUT_TYPES_ALIASES_RUS[result_type]

    text = (
        f'РЕЗУЛЬТАТ ТРЕНИРОВКИ\n\n'
        f'Гребец: {user_name}\n'
        f'Дата: {result_date:%d.%m.%y}\n'
        f'Тип тренировки: {type_ru}\n\n'
        f'Текст:\n{result_text}\n\n'
        f'Ссылка на фото: {result_url}'
    )
    
    results_list = DBUser.get_results_of_user(user_telegram_id)
    for result in results_list:
        if result.date == result_date:
            result_id = result.id
    
    for admin in admin_list:
        try:
            await context.bot.send_message(
                chat_id=admin.telegram_id, 
                text=text,
                reply_markup=await AdminKeyboard.generate_admin_result_keyboard(result_id),
            )
        except (TelegramError, Forbidden) as error:
            LOGGER.error(
                'Ошибка при попытке отправить результат тренировки администратору.\n'
                f'\tTG ID: {admin.telegram_id}; admin first_name и last_name: {admin.first_name} {admin.last_name}\n'
                f'\tТекст ошибки: {error.message}'
            )

    await message.reply_text('Результат успешно отправлен!')

    return ConversationHandler.END


send_result_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(on_click_send_result, 'menu_user_send_result')],
    states={
        UserStates.TYPING_RESULT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_result_type)],
        UserStates.TYPING_RESULT_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_result_text)],
        UserStates.TYPING_RESULT_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_result_url)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
