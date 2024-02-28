from telegram import Update, Message
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from tgbot.handlers.commands import cancel
from tgbot.interface.buttons.user import on_click_change_number_training_days
from tgbot.json import get_recommendation
from tgbot.states import UserStates
from tgbot.database import DBUser
from config import MIN_NUMBER_OF_TRAINING_DAYS, MAX_NUMBER_OF_TRAINING_DAYS


async def receive_date_settings(update: Update, _):
    message: Message = update.message 

    try:
        number_training_days = int(update.message.text.strip()) 
    except ValueError:
        await message.reply_text('Ой! Кажется, вы не поняли. Введите целое число, означающее количество тренировок в неделе.')

        return UserStates.TYPING_DAYS
    
    if number_training_days not in range(MIN_NUMBER_OF_TRAINING_DAYS, MAX_NUMBER_OF_TRAINING_DAYS + 1):
        await message.reply_text(f'Количество тренировочных дней должно быть от {MIN_NUMBER_OF_TRAINING_DAYS} до {MAX_NUMBER_OF_TRAINING_DAYS}. Попробуйте ещё раз:')

        return UserStates.TYPING_DAYS 

    DBUser.update_user(
        telegram_id=message.from_user.id, 
        number_training_days=number_training_days
    )

    await message.reply_text(f'Количество тренировок в неделю изменено на {number_training_days}.')

    recommendation = get_recommendation(number_training_days)

    if recommendation is None:
        recommendation = 'Упс! Тут должна быть рекомендация по тренировкам, но что-то пошло не так, обратись к тренеру.'

    await message.reply_markdown_v2(f'Рекомендация по тренировкам \({number_training_days} дней\):\n```\n{recommendation}\n```')

    return ConversationHandler.END


change_days_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(on_click_change_number_training_days, 'menu_user_number_training_days')],
    states={
        UserStates.TYPING_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_date_settings)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
