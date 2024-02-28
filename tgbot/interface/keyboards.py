'''Содержит обёртки клавиатур пользователя и админа, а также генераторы клавиатур'''
from typing import Optional

from telegram import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup

from tgbot.database import DBUser, DBWorkout
from config import WORKOUT_TYPES_ALIASES_RUS


class UserKeyboard:
    '''Содержит клавиатуры пользователя'''
    MENU: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton('Тренировки'),
                KeyboardButton('Календарь соревнований'),
            ],
            [
                KeyboardButton('FAQ'),
                KeyboardButton('Настройки'),
            ],
        ], 
        resize_keyboard=True
    )

    TRAINING: InlineKeyboardMarkup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Выполненные тренировки', callback_data='menu_user_completed_workouts')
        ],
        [
            InlineKeyboardButton('Начать тренировку', callback_data='menu_user_start_training')
        ],
    ])

    WORKOUT: InlineKeyboardMarkup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Я заболел', callback_data='menu_user_disease')
        ],
        [
            InlineKeyboardButton('Сила', callback_data='menu_user_strength'),
            InlineKeyboardButton('Выносливость', callback_data='menu_user_endurance'),
        ],
        [
            InlineKeyboardButton('Скорость', callback_data='menu_user_speed'),
            InlineKeyboardButton('Восстановление', callback_data='menu_user_recovery'),
        ],
    ])

    SETTINGS: InlineKeyboardMarkup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Изменить количество тренировок в неделе', callback_data='menu_user_number_training_days'),
        ],
        [
            InlineKeyboardButton('Изменить имя', callback_data='menu_user_first_name'),
            InlineKeyboardButton('Изменить фамилию', callback_data='menu_user_last_name'),
        ],
    ])

    SEND_RESULT: InlineKeyboardMarkup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Отправить результат тренировки', callback_data='menu_user_send_result')
        ],
    ])


class AdminKeyboard:
    '''Содержит клавиатуры и методы для создания клавиатур администратора'''
    MENU: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton('Гребцы'),
                KeyboardButton('Настройки'),
            ],
        ], 
        resize_keyboard=True
    )

    SETTINGS: InlineKeyboardMarkup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Календарь соревнований', callback_data='menu_admin_calendar'),
            InlineKeyboardButton('FAQ', callback_data='menu_admin_faq'),
        ],
        [
            InlineKeyboardButton('Тренировки', callback_data='menu_admin_training'),
        ],
        [
            InlineKeyboardButton('Изменить пароль администратора', callback_data='menu_admin_change_password'),
        ],
    ])

    TRAINING: InlineKeyboardMarkup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Список тренировок', callback_data='menu_admin_list_of_workouts'),
            InlineKeyboardButton('Добавить тренировку', callback_data='menu_admin_add_workout'),
        ]
    ])

    @classmethod
    async def generate_rowers_keyboard(cls) -> Optional[InlineKeyboardMarkup]:
        rowers_keyboard: list[list[InlineKeyboardButton]] = []
        users = DBUser.get_users()

        if users is None:
            return None
        
        row_of_buttons: list[InlineKeyboardButton] = []
        for counter, user in enumerate(users, start=1):
            button_text = f'{user.last_name} {user.first_name}'
            button_callback_data = f'rower_{user.telegram_id}'
            await cls.__add_button_in_row_of_buttons(row_of_buttons, button_text, button_callback_data)

            is_second_in_row = counter % 2 == 0
            if is_second_in_row:
                await cls.__add_row_of_buttons_to_keyboard(rowers_keyboard, row_of_buttons)
                row_of_buttons = []

        if row_of_buttons:
            await cls.__add_row_of_buttons_to_keyboard(rowers_keyboard, row_of_buttons)
        
        return InlineKeyboardMarkup(rowers_keyboard)

    @classmethod
    async def generate_workouts_keyboard(cls) -> Optional[InlineKeyboardMarkup]:
        workouts_keyboard: list[list[InlineKeyboardButton]] = []
        workouts = DBWorkout.get_workouts()

        if workouts is None:
            return None
        
        row_of_buttons: list[InlineKeyboardButton] = []
        for counter, workout in enumerate(workouts, start=1):
            button_text = f'{WORKOUT_TYPES_ALIASES_RUS.get(workout.type)} {workout.name}' 
            button_callback_data = f'workout_{workout.id}'
            await cls.__add_button_in_row_of_buttons(row_of_buttons, button_text, button_callback_data)

            is_second_in_row = counter % 2 == 0
            if is_second_in_row:
                await cls.__add_row_of_buttons_to_keyboard(workouts_keyboard, row_of_buttons)
                row_of_buttons = []

        if row_of_buttons:
            await cls.__add_row_of_buttons_to_keyboard(workouts_keyboard, row_of_buttons)
        
        return InlineKeyboardMarkup(workouts_keyboard)
    
    @classmethod
    async def generate_available_workout_types(cls) -> InlineKeyboardMarkup:
        available_workouts_keyboard: list[list[InlineKeyboardButton]] = []
        available_workouts = WORKOUT_TYPES_ALIASES_RUS.items()

        row_of_buttons: list[InlineKeyboardButton] = []
        for counter, workout_alias in enumerate(available_workouts, start=1):
            workout_in_english, workout_in_russian = workout_alias

            await cls.__add_button_in_row_of_buttons(
                row_of_buttons,
                button_text=workout_in_russian,
                button_callback_data=f'workout_type_{workout_in_english}',
            )

            is_second_in_row = counter % 2 == 0
            if is_second_in_row:
                await cls.__add_row_of_buttons_to_keyboard(available_workouts_keyboard, row_of_buttons)
                row_of_buttons = []

        if row_of_buttons:
            await cls.__add_row_of_buttons_to_keyboard(available_workouts_keyboard, row_of_buttons)
        
        return InlineKeyboardMarkup(available_workouts_keyboard)

    
    @classmethod
    async def generate_results_keyboard(cls, user_telegram_id: int) -> Optional[InlineKeyboardMarkup]:
        results_keyboard: list[list[InlineKeyboardButton]] = []
        results_list = DBUser.get_results_of_user(user_telegram_id) 

        if results_list is None:
            return None
        
        row_of_buttons: list[InlineKeyboardButton] = []
        for counter, result in enumerate(results_list, start=1):
            button_text = f'ID: {result.id}▪️{result.date:%d.%m.%y}▪️{"✅" if result.is_accepted else "❌"}'
            button_callback_data = f'result_{result.id}'
            await cls.__add_button_in_row_of_buttons(row_of_buttons, button_text, button_callback_data)

            is_second_in_row = counter % 2 == 0
            if is_second_in_row:
                await cls.__add_row_of_buttons_to_keyboard(results_keyboard, row_of_buttons)
                row_of_buttons = []

        if row_of_buttons:
            await cls.__add_row_of_buttons_to_keyboard(results_keyboard, row_of_buttons)
        
        return InlineKeyboardMarkup(results_keyboard)

    @staticmethod
    async def generate_chosen_rower_keyboard(user_telegram_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Удалить', callback_data=f'menu_admin_delete_rower_{user_telegram_id}'),
                InlineKeyboardButton('Посещаемость', callback_data=f'menu_admin_rower_attedance_{user_telegram_id}'),
            ],
            [
                InlineKeyboardButton('Назначить админом', callback_data=f'menu_admin_make_new_admin_{user_telegram_id}'),
            ],
        ])

    @staticmethod
    async def generate_chosen_workout_keyboard(workout_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Удалить тренировку', callback_data=f'menu_admin_delete_workout_{workout_id}')
            ]
        ])

    @staticmethod
    async def generate_admin_result_keyboard(result_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Принять', callback_data=f'menu_admin_accept_result_{result_id}'),
                InlineKeyboardButton('Отклонить', callback_data=f'menu_admin_reject_result_{result_id}'),
            ]
        ])
    
    @staticmethod
    async def __create_button(button_text: str, button_callback_data: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(button_text, callback_data=button_callback_data)

    @classmethod
    async def __add_button_in_row_of_buttons(cls, row_of_buttons: list, button_text: str, button_callback_data: str) -> None:
        button = await cls.__create_button(button_text, button_callback_data)

        row_of_buttons.append(button)

    @staticmethod
    async def __add_row_of_buttons_to_keyboard(keyboard: list, row_of_buttons: list) -> None:
        keyboard.append(row_of_buttons)
