'''Содержит функции, которые должны исполняться по нажатию кнопок пользователя'''
import random
import logging

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from config import FILENAME_FAQ, FILENAME_CALENDAR, WORKOUT_TYPES_ALIASES_RUS, MIN_NUMBER_OF_TRAINING_DAYS, MAX_NUMBER_OF_TRAINING_DAYS
from tgbot.interface.keyboards import UserKeyboard
from tgbot.json import get_recommendation
from tgbot.states import UserStates
from tgbot.database import DBUser, DBWorkout


LOGGER = logging.getLogger()


async def on_click_training(update: Update, _):
    reply_markup = UserKeyboard.TRAINING

    await update.message.reply_text( 
        'Здесь ты можешь посмотреть выполненные тренировки или начать тренировку!',
        reply_markup=reply_markup,
    )


async def on_click_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(FILENAME_CALENDAR, "r", encoding="utf-8") as file:
        calendar_content = file.read()

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=calendar_content,
    )


async def on_click_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(FILENAME_FAQ, "r", encoding="utf-8") as file:
        faq_content = file.read()

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=faq_content,
    )


async def on_click_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = UserKeyboard.SETTINGS

    user = DBUser.get_user(update.effective_chat.id)

    days = user.number_training_days
    first_name = user.first_name
    last_name = user.last_name

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text= (f'⚙️ Настройки\n'
               f'Выберите параметр, который желаете настроить:\n'
               f'-Фамилия: {last_name}\n'
               f'-Имя: {first_name}\n'
               f'-Количество тренировок в неделе: {days}\n'),
        reply_markup=reply_markup,
    )


async def on_click_completed_workouts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_chat.id
    results_list = DBUser.get_results_of_user(telegram_id)
    text = 'Выполненные тренировки:\n'
    
    if results_list:
        for i, result in enumerate(results_list, start=1):
            type_ru = WORKOUT_TYPES_ALIASES_RUS[result.type] 
            text += f'{i}) {result.date:%d.%m.%y}: {type_ru}\n{result.url}\n{result.text}\n\n'
    else:
        text = 'Вы еще не выполнили ни одной тренировки!'

    await context.bot.send_message(
            chat_id=telegram_id, 
            text=text,
        )
        

async def on_click_start_training(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number_training_days = DBUser.get_user(update.effective_chat.id).number_training_days
    
    recommendation = get_recommendation(number_training_days)

    if recommendation is None:
        recommendation = 'Упс! Тут должна быть рекомендация по тренировкам, но что-то пошло не так, обратись к тренеру.'

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f'Рекомендация по тренировкам ({number_training_days} дней):\n{recommendation}',
    )
    reply_markup = UserKeyboard.WORKOUT
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Выберите тренировку:',
        reply_markup=reply_markup,
    )


async def on_click_disease(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = DBUser.get_user(update.effective_chat.id) 
    user_name = f'{user.first_name} {user.last_name}' 
    admin_list = DBUser.get_admins()

    if admin_list is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text='На данный момент администраторов бота нет, оповестите тренера о состоянии вашего здоровья самостоятельно.',
        )
        return
    
    for admin in admin_list:
        admin_telegram_id = admin.telegram_id

        try:
            await context.bot.send_message(
                chat_id=admin_telegram_id, 
                text=f'{user_name} заболел.',
            )
        except TelegramError as error:
            LOGGER.error(
                f'Ошибка при попытке отправить уведомление администратору при оповещении о болезни спортсмена {user.last_name} {user.first_name}.\n' 
                f'\tТекст ошибки: {admin.last_name} {admin.first_name}: {error.message}' 
            )

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Очень жаль, что ты заболел, я оповестил всех тренеров, выздоравливай!',
    )


async def on_click_send_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Введите тип тренировки:",
    )

    return UserStates.TYPING_RESULT_TYPE


async def on_click_display_workout(update: Update, context: ContextTypes.DEFAULT_TYPE, type: str):
    workouts = DBWorkout.get_workouts(type)
    
    if workouts:
        reply_markup = UserKeyboard.SEND_RESULT
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=random.choice(workouts).text, 
            reply_markup=reply_markup,
        )
        return
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Админ еще не добавил тренировки данного типа!',
    )


async def on_click_strength(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await on_click_display_workout(update, context, 'strength')


async def on_click_endurance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await on_click_display_workout(update, context, 'endurance')


async def on_click_speed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await on_click_display_workout(update, context, 'speed')


async def on_click_recovery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await on_click_display_workout(update, context, 'recovery')


async def on_click_change_number_training_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f'Введите желаемое количество тренировок в неделе (от {MIN_NUMBER_OF_TRAINING_DAYS} до {MAX_NUMBER_OF_TRAINING_DAYS}):',
    )

    return UserStates.TYPING_DAYS


async def on_click_change_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Введите ваше имя:',
    )

    return UserStates.TYPING_FIRST_NAME


async def on_click_change_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Введите вашу фамилию:',
    )
    
    return UserStates.TYPING_LAST_NAME


TEXT_BUTTONS_PARSER = {
    'Тренировки': on_click_training,
    'Календарь соревнований': on_click_calendar,
    'FAQ': on_click_faq,
    'Настройки': on_click_settings,
}


CALLBACK_BUTTONS_PARSER = {
    'menu_user_completed_workouts': on_click_completed_workouts,
    'menu_user_start_training': on_click_start_training,
    'menu_user_disease': on_click_disease,
    'menu_user_strength': on_click_strength,
    'menu_user_endurance': on_click_endurance,
    'menu_user_speed': on_click_speed,
    'menu_user_recovery': on_click_recovery,
}
