'''Предоставляет инструменты для обработки отправляемых команд'''
from datetime import time

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from tgbot.database import DBUser
from tgbot.notifications import user_check_trainings, admin_check_trainings


async def cancel(update: Update, _):
    await update.message.reply_markdown('Действие отменено.') 

    return ConversationHandler.END


async def exit_bot(update: Update, _):
    DBUser.delete_user(update.message.from_user.id) 
    
    await update.message.reply_text('Вы были удалены из базы данных пользователей. Уведомления вам больше присылаться не будут') 


async def set_jobs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id: int = update.message.from_user.id 

    user = DBUser.get_user(telegram_id)

    if user is None:
        await update.message.reply_text('Вы не зарегистрированы!\nДля регистрации введите команду /start')
        return

    if not user.is_admin: 
        await update.message.reply_text('Данную команду может выполнить только администратор!') 
        return

    job_queue = context.application.job_queue
    current_jobs = job_queue.jobs() 

    if current_jobs:
        for job in current_jobs:
            job.schedule_removal()

    job_time = time(hour=5, minute=0) # NOTE: Часовой пояс UTC, в СПБ будет 05:00+03:00, то есть 08:00
    days_for_user_check_trainings = (0, 2, 3, 4, 5, 6) # NOTE: вс, вт, ср, чт, пт, сб
    job_queue.run_daily(user_check_trainings, job_time, days=days_for_user_check_trainings, name='user_morning_check_trainings') 

    job_time = time(hour=15, minute=0)
    job_queue.run_daily(user_check_trainings, job_time, days=days_for_user_check_trainings, name='user_evening_check_trainings') 

    job_time = time(hour=16, minute=0)
    days_for_admin_check_trainings = (0, )
    job_queue.run_daily(admin_check_trainings, job_time, days=days_for_admin_check_trainings, name='admin_check_trainings') 
 
    await update.message.reply_text('Уведомления были запущены!') 
