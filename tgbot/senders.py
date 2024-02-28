'''Отдельные функции, используемые для отправки'''
import logging

from telegram.ext import ContextTypes
from telegram.error import TelegramError, Forbidden

from tgbot.database import DBUser


LOGGER = logging.getLogger()


async def send_message_to_admins(message: str, context: ContextTypes.DEFAULT_TYPE):
    admins = DBUser.get_admins()

    if admins is None:
        LOGGER.debug('Database do not have admins. Failed attempt to send message to admins.')
        return

    for admin in admins:
        try:
            await context.bot.send_message(admin.telegram_id, message)
        except (TelegramError, Forbidden) as error:
            LOGGER.error(
                'Ошибка при попытке отправить уведомления администраторам при проверке результатов пользователей.\n'
                f'\tTG ID: {admin.telegram_id}; admin first_name и last_name: {admin.first_name} {admin.last_name}\n'
                f'\tТекст ошибки: {error.message}'
            )
