from telegram import Update, Message
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, ContextTypes

from tgbot.database import DBUser
from tgbot.interface.menu import start_user_menu
from tgbot.handlers.commands import cancel
from tgbot.states import UserStates
from tgbot.json import get_recommendation
from config import MAX_NUMBER_OF_TRAINING_DAYS, MIN_NUMBER_OF_TRAINING_DAYS, URL_FORMS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message 

    await message.reply_text(
        '🚣 Привет! Я - бот Polyrow, ваш помощник в тренировках по гребле!'
    )

    telegram_id: int = message.from_user.id 
    if DBUser.contains_user(telegram_id):
        if DBUser.get_user(telegram_id).is_admin:
            await message.reply_text('💆‍♂️ Переключение в режим пользователя!')
            DBUser.set_admin(telegram_id, set=False)
        await start_user_menu(update, context)
        
        return ConversationHandler.END
    
    await message.reply_text(
        '📋 Пожалуйста, пройдите быструю регистрацию, мне важно знать информацию о вас.\n'
        'Для отмены регистрации просто напишите /cancel.'
    )

    await message.reply_text('1️⃣ Напишите вашу фамилию:')

    return UserStates.TYPING_LAST_NAME


async def receive_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message 

    context.user_data['last_name'] = message.text.strip() 

    await message.reply_text('2️⃣ Введите ваше имя:')
    
    return UserStates.TYPING_FIRST_NAME


async def receive_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message 

    context.user_data['first_name'] = message.text.strip() 

    await message.reply_text(f'3️⃣ Введите количество дней тренировок в неделе от {MIN_NUMBER_OF_TRAINING_DAYS} до {MAX_NUMBER_OF_TRAINING_DAYS}:')

    return UserStates.TYPING_DAYS


async def receive_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message 

    try:
        number_training_days = int(update.message.text.strip()) 
    except ValueError:
        await message.reply_text(
            '🥴 Ой! Кажется, вы не поняли.\n'
            'Введите целое число, означающее количество тренировок в неделе.'
        )

        return UserStates.TYPING_DAYS
    
    if number_training_days not in range(MIN_NUMBER_OF_TRAINING_DAYS, MAX_NUMBER_OF_TRAINING_DAYS + 1):
        await message.reply_text(
            '🥴 Ой! Кажется, вы не поняли.\n'
            f'Количество тренировочных дней должно быть от {MIN_NUMBER_OF_TRAINING_DAYS} до {MAX_NUMBER_OF_TRAINING_DAYS}.'
        )
        
        await message.reply_text('Попробуйте ещё раз:')

        return UserStates.TYPING_DAYS 

    DBUser.create_user(
        telegram_id=message.from_user.id, 
        first_name=context.user_data['first_name'], 
        last_name=context.user_data['last_name'], 
        number_training_days=number_training_days
    )

    await message.reply_text('🎉 Регистрация в боте завершена успешно.')
    await message.reply_text(f'📃 Теперь, пожалуйста, заполните анкету: {URL_FORMS}.')

    recommendation = get_recommendation(number_training_days)
    if recommendation is None:
        recommendation = '🥴 Упс! Тут должна быть рекомендация по тренировкам, но что-то пошло не так, обратитесь к тренеру.'
        # TODO: "...к тренеру или администратору." Реализовать летом в кнопке FAQ при нажатии на вопрос об администраторах вывод списка с ними
    
    await message.reply_text(
        '🤩 Кстати! Держите персональную рекомендацию!\n'
        'Она поможет вам определить, как вам лучше тренироваться в течение недели!\n'
        'Не волнуйтесь, если ее забудете, вы всегда сможете найти её в...' # TODO: Дописать, где найти тренировку
    )
    await message.reply_markdown_v2(f'Рекомендация по тренировкам \(дней на тренировки: {number_training_days}\):\n```\n{recommendation}\n```')
    
    await start_user_menu(update, context)

    return ConversationHandler.END


auth_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        UserStates.TYPING_FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_first_name)],
        UserStates.TYPING_LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_last_name)],
        UserStates.TYPING_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_date)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)