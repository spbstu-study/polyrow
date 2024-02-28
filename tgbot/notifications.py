'''Модуль, реализующий проверку на активность'''
import logging
from datetime import datetime, timedelta

from telegram.ext import ContextTypes
from telegram.error import TelegramError, Forbidden

from tgbot.database import DBUser
from tgbot.senders import send_message_to_admins


LOGGER = logging.getLogger()


def is_date_this_week(date):
    today = datetime.now()

    start_of_week = today - timedelta(days=today.weekday(), minutes=today.minute, hours=today.hour)
    end_of_week = start_of_week + timedelta(days=6, minutes=59, hours=23)

    return start_of_week <= date <= end_of_week


async def admin_check_trainings(context: ContextTypes.DEFAULT_TYPE):
    users = DBUser.get_users()

    if users is None:
        return

    for user in users:
        if user.is_admin:
            continue

        zero_accepted_trainings = True

        results = DBUser.get_results_of_user(user.telegram_id)

        if results is None:
            continue

        for result in results: 
                if all((is_date_this_week(result.date), result.is_accepted)):
                    zero_accepted_trainings = False
                    break

        if zero_accepted_trainings:
            message = f'ЕЖЕНЕДЕЛЬНАЯ ПРОВЕРКА АКТИВНОСТИ ПОЛЬЗОВАТЕЛЕЙ\n\nУ пользователя {user.first_name} {user.last_name} 0 принятых тренировок.'
            await send_message_to_admins(message, context) 


async def user_check_trainings(context: ContextTypes.DEFAULT_TYPE):
    users = DBUser.get_users()

    if users is None:
        return
    
    for user in users:
        if user.is_admin:
            continue

        results = DBUser.get_results_of_user(user.telegram_id) 

        if results is None:
            continue
        
        number_of_results = 0
        for result in results: 
            if is_date_this_week(result.date):
                number_of_results += 1
        
        number_of_trainings_to_do = user.number_training_days - number_of_results 
        number_of_days_left_in_week = 7 - datetime.now().weekday()
        if number_of_trainings_to_do == number_of_days_left_in_week:
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id, 
                    text='ЕЖЕДНЕВНАЯ ПРОВЕРКА НА АКТИВНОСТЬ\n\nВы тренировались недостаточно на этой неделе.\n'
                        f'Осталось прислать результатов тренировок: {number_of_trainings_to_do}',
                )
            except (TelegramError, Forbidden) as error:
                LOGGER.error(
                    'Ошибка при попытке отправить уведомление пользователю при проверке кол-ва дней оставшихся тренировок в неделе.\n'
                    f'\tTG ID: {user.telegram_id}; first_name и last_name: {user.first_name} {user.last_name}\n'
                    f'\tТекст ошибки: {error.message}' 
                )
