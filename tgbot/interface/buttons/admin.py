'''Содержит функции, которые должны исполняться по нажатию кнопок администратора'''
from typing import Callable

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from config import FILENAME_FAQ, FILENAME_CALENDAR, WORKOUT_TYPES_ALIASES_RUS
from tgbot.json import get_password
from tgbot.database import DBUser, DBWorkout, DBResult
from tgbot.interface.keyboards import AdminKeyboard
from tgbot.getters import get_id
from tgbot.interface.menu import start_admin_menu
from tgbot.states import AdminStates


async def on_click_rowers(update: Update, _):
    reply_markup = await AdminKeyboard.generate_rowers_keyboard()

    if reply_markup is None:
        await update.message.reply_text('Пока что в боте не зарегистрирован ни один гребец!')
        return

    await update.message.reply_text( 
        'Список гребцов:',
        reply_markup=reply_markup,
    )


async def on_click_rower(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = get_id(update.callback_query.data) 
    reply_markup = await AdminKeyboard.generate_chosen_rower_keyboard(telegram_id) 
    user = DBUser.get_user(telegram_id) 

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f'Выбран гребец {user.last_name} {user.first_name}', 
        reply_markup=reply_markup,
    )


async def on_click_delete_rower(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = get_id(update.callback_query.data) 
    user = DBUser.get_user(telegram_id) 

    DBUser.delete_user(telegram_id) 

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f'{user.last_name} {user.first_name} удалён(-ена) из базы данных пользователей!', 
    )


async def on_click_rower_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = get_id(update.callback_query.data)
    user = DBUser.get_user(telegram_id)
    reply_markup = await AdminKeyboard.generate_results_keyboard(telegram_id)
    results_list = DBUser.get_results_of_user(telegram_id) 

    if reply_markup is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Спортсмен "{user.last_name} {user.first_name}" не прислал ни одного результата тренировки!',
        )
        return
    
    accepted_workouts = list(filter(lambda result: result.is_accepted, results_list))
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f'Всего отправлено результатов тренировок: {len(results_list)}\n'
            f'Количество зачтённых тренировок: {len(accepted_workouts)}\n\n'
            f'Список результатов тренировок гребца "{user.last_name} {user.first_name}":'
        ),
        reply_markup=reply_markup,
    )


async def on_click_rower_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result_id = get_id(update.callback_query.data)
    result = DBResult.get_result(result_id)
    user = result.user
    reply_markup = await AdminKeyboard.generate_admin_result_keyboard(result_id)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=(
            f'РЕЗУЛЬТАТ ТРЕНИРОВКИ\n\n'
            f'Cтатус: {"Принято" if result.is_accepted else "Отклонено"}\n'
            f'Гребец: {user.last_name} {user.first_name}\n'
            f'Дата: {result.date:%d.%m.%y}\n'
            f'Тип тренировки: {WORKOUT_TYPES_ALIASES_RUS.get(result.type)}\n\n'
            f'Текст:\n{result.text}\n\n'
            f'Ссылка на фото: {result.url}'
        ),
        reply_markup=reply_markup,
    )


async def on_click_make_new_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = get_id(update.callback_query.data) 
    user = DBUser.get_user(telegram_id) 

    if user.is_admin: 
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=f'{user.last_name} {user.first_name} уже является администратором!', 
        )
        return

    try:
        await start_admin_menu(update, context, chat_id=telegram_id) 
    except TelegramError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=f'Я не могу назначить пользователя {user.last_name} {user.first_name} администратором. Проверьте зарегестрирован ли он в Telegram.', 
        )
        return

    DBUser.set_admin(telegram_id, set=True) 
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f'{user.last_name} {user.first_name} теперь администратор.', 
    )


async def on_click_settings(update: Update, _):
    reply_markup = AdminKeyboard.SETTINGS

    await update.message.reply_text( 
        'Настройки:',
        reply_markup=reply_markup,
    )


async def on_click_change_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(FILENAME_CALENDAR, "r", encoding="utf-8") as file:
        calendar_content = file.read()

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f'Старый текст:\n{calendar_content}',
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Введите новый текст:\n(команда /cancel для отмены)',
    )

    return AdminStates.TYPING_CALENDAR


async def on_click_change_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(FILENAME_FAQ, "r", encoding="utf-8") as file:
        faq_content = file.read()
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f'Старый текст:\n{faq_content}',
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Введите новый текст:\n(команда /cancel для отмены)',
    )
    
    return AdminStates.TYPING_FAQ


async def on_click_training(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = AdminKeyboard.TRAINING

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Управление тренировками:',
        reply_markup=reply_markup,
    )


async def on_click_workouts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = await AdminKeyboard.generate_workouts_keyboard()

    if reply_markup is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Пока что в базу данных не была добавлена ни одна тренировка!',
        )
        return
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Выберите тренировку:',
        reply_markup=reply_markup,
    )


async def on_click_change_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = get_password()

    if password:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=f'Старый пароль:\n{password}',
        ) 

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f'Введите новый пароль:\n(команда /cancel для отмены)',
        )

    return AdminStates.TYPING_NEW_PASSWORD


async def on_click_add_workout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = await AdminKeyboard.generate_available_workout_types()
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Выберите тип тренировки:\n(введите /cancel для отмены)",
        reply_markup=reply_markup,
    )

    return AdminStates.WORKOUT_TYPING_TYPE


async def on_click_workout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    workout_id = get_id(update.callback_query.data) 
    reply_markup = await AdminKeyboard.generate_chosen_workout_keyboard(workout_id) 
    workout = DBWorkout.get_workout(workout_id) 

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=(
            f'{WORKOUT_TYPES_ALIASES_RUS.get(workout.type).upper()}\n\n'
            f'Название тренировки: "{workout.name}"\n'
            f'Дата создания: "{workout.creation_date:%d.%m.%y}"\n\n'
            f'Текст тренировки:\n{workout.text}'
        ), 
        reply_markup=reply_markup,
    )


async def on_click_delete_workout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    workout_id = get_id(update.callback_query.data) 

    DBWorkout.delete_workout(workout_id) 

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Тренировка успешно удалена из базы данных!',
    )


async def on_click_accept_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    DBResult.update_result(
        result_id=get_id(update.callback_query.data),
        is_accepted=True,
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Результат тренировки принят!',
    )
    

async def on_click_reject_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    DBResult.update_result(
        result_id=get_id(update.callback_query.data),
        is_accepted=False,
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Результат тренировки отклонён!',
    )


TEXT_BUTTONS_PARSER: dict[str, Callable] = {
    'Гребцы': on_click_rowers,
    'Настройки': on_click_settings,
}


CALLBACK_BUTTONS_PARSER: dict[str, Callable] = {
    'rower': on_click_rower,
    'workout': on_click_workout,
    'result': on_click_rower_result,
    'menu_admin_delete_rower': on_click_delete_rower,
    'menu_admin_rower_attedance': on_click_rower_attendance,
    'menu_admin_make_new_admin': on_click_make_new_admin,
    'menu_admin_calendar': on_click_change_calendar,
    'menu_admin_faq': on_click_change_faq,
    'menu_admin_training': on_click_training,
    'menu_admin_list_of_workouts': on_click_workouts,
    'menu_admin_delete_workout': on_click_delete_workout,
    'menu_admin_accept_result': on_click_accept_result,
    'menu_admin_reject_result': on_click_reject_result,
}
