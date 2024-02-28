import re

from telegram import Update, Message
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from tgbot.handlers.commands import cancel
from tgbot.interface.buttons.admin import on_click_add_workout
from tgbot.states import AdminStates
from config import WORKOUT_TYPES_ALIASES_RUS
from tgbot.database import DBWorkout


async def _get_workout_type(callback_data: str, separator: str = '_') -> str:
    return callback_data.split(separator)[-1]


async def receive_workout_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    workout_type = await _get_workout_type(update.callback_query.data)

    if WORKOUT_TYPES_ALIASES_RUS.get(workout_type):
        context.user_data['workout_type'] = workout_type

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Придумай любое название для тренировки:\n(введите /cancel для отмены)',
        )

        return AdminStates.WORKOUT_TYPING_NAME

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Такого типа тренировок я не знаю. Попробуйте ещё раз или введите команду отмены /cancel',
    )

    return AdminStates.WORKOUT_TYPING_TYPE


async def receive_workout_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message 

    context.user_data['workout_name'] = message.text.strip() 

    await message.reply_text('Введите текст тренировки:\n(введите /cancel для отмены)')

    return AdminStates.WORKOUT_TYPING_TEXT


async def receive_workout_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message 

    context.user_data['workout_text'] = message.text.strip() 

    DBWorkout.create_workout(
        type=context.user_data['workout_type'], 
        name=context.user_data['workout_name'], 
        text=context.user_data['workout_text'], 
    )

    await message.reply_text('Тренировка успешно добавлена!')

    return ConversationHandler.END


add_workout_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(on_click_add_workout, 'menu_admin_add_workout')],
    states={
        AdminStates.WORKOUT_TYPING_TYPE: [CallbackQueryHandler(receive_workout_type, re.compile('workout_type_\S*'))],
        AdminStates.WORKOUT_TYPING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_workout_name)],
        AdminStates.WORKOUT_TYPING_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_workout_text)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
