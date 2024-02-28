import logging

from telegram.ext import (
    Application,
    ApplicationBuilder,
    JobQueue,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
)

from config import BOT_TOKEN
from tgbot.handlers.commands import exit_bot, set_jobs_command
from tgbot.handlers.buttons import handle_reply_button, handle_inline_button
from tgbot.handlers.conversations import (
    auth_handler, admin_handler, send_result_handler, add_workout_handler,
    change_first_name_handler, change_last_name_handler, change_days_handler, change_password_handler, 
    change_calendar_handler, change_faq_handler, mailing_handler
)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)


def main():
    application: Application = ApplicationBuilder().token(BOT_TOKEN).build()
    job_queue: JobQueue = JobQueue()
    job_queue.set_application(application)

    # NOTE: Следите за порядком обработчиков: сначала обработчики команд, потом диалоговые обработчики, потом обработчики кнопок
    application.add_handlers([
        CommandHandler('exit', exit_bot),
        CommandHandler('setjobs', set_jobs_command),
        auth_handler,
        admin_handler,
        mailing_handler,
        send_result_handler,
        add_workout_handler,
        change_first_name_handler,
        change_last_name_handler, 
        change_days_handler, 
        change_password_handler,
        change_calendar_handler,
        change_faq_handler,
        MessageHandler(filters.TEXT, handle_reply_button),
        CallbackQueryHandler(handle_inline_button),
    ])

    application.run_polling()


if __name__ == '__main__':
    main()
