from typing import Optional

from peewee import DoesNotExist

from tgbot.database.models import UserModel, ResultModel
from tgbot.database.wrappers.user import User
from tgbot.database.wrappers.result import Result
from tgbot.database.api.dbobj import DBObject


class DBUser(DBObject):
    '''Предоставляет методы для работы с пользователями в базе данных'''
    @staticmethod
    def contains_user(telegram_id: int) -> bool:
        '''Проверить, есть ли в базе данных пользователь с заданным Telegram ID
        
        Args:
            telegram_id: 
                Telegram ID пользователя.

        Returns:
            :obj:`bool`: Состояние нахождения в базе данных.
        '''
        try:
            UserModel.get(UserModel.telegram_user_id == telegram_id)
            return True
        except DoesNotExist:
            return False
    
    @classmethod
    def create_user(cls, telegram_id: int, first_name: str, last_name: str, number_training_days: int, is_admin: bool = False) -> None:
        '''Создать и добавить пользователя в базу данных.
        
        Создаёт пользователя в базе, используя такие же параметры, как в обёртке :class:`tgbot.database.wrappers.DBUser`.

        Args:
            telegram_id: 
                Telegram ID пользователя.
            first_name: 
                Имя пользователя.
            last_name: 
                Фамилия пользователя.
            number_training_days: 
                Количество тренировок в неделе.
            is_admin: 
                Если True, пользователь - администратор.

        Raises:
            Exception: There is already a user with this id {telegram_id} in the database.
        '''
        if cls.contains_user(telegram_id):
            raise Exception(f'There is already a user with this id {telegram_id} in the database')
        UserModel.create(
            telegram_user_id=telegram_id, 
            first_name=first_name,
            last_name=last_name,
            training_days=number_training_days,
            is_admin=is_admin
        )

    @classmethod
    def update_user(cls, telegram_id: int, first_name: Optional[str] = None, last_name: Optional[str] = None, 
                number_training_days: Optional[int] = None, is_admin: Optional[bool] = None) -> bool:
        '''Обновить пользователя в базе данных.

        Обновляет пользователя в базе по его Telegram ID, используя параметры, как в обёртке :class:`tgbot.database.wrappers.DBUser`.
        
        .. attention::
            Обязательно нужно передавать хотя бы один аргумент для изменения, иначе возникает исключение.
        
        Args:
            telegram_id: 
                Telegram ID пользователя.
            first_name: 
                Имя пользователя.
            last_name: 
                Фамилия пользователя.
            number_training_days: 
                Количество тренировок в неделе.
            is_admin: 
                Если True, пользователь - администратор.

        Returns:
            :obj:`bool`: Состояние выполнения функции (False - пользователь не найден). 

        Raises:
            ValueError: No argument was passed to the function, at least one is required.
        '''
        if not cls.contains_user(telegram_id):
            return False

        params = {
            'first_name': first_name,
            'last_name': last_name,
            'training_days': number_training_days,
            'is_admin': is_admin
        }

        params = {k: v for k, v in params.items() if v is not None}

        if not params:
            raise ValueError('No argument was passed to the function, at least one is required')

        query = UserModel.update(params).where(UserModel.telegram_user_id == telegram_id)
        query.execute()
        
        return True
    
    @classmethod
    def set_admin(cls, telegram_id: int, set: bool = True) -> bool:
        '''Установить параметр администратора у пользователя.
        
        Устанавливает параметр администратора у пользователя и является узконаправленной
        версией функции обновления пользователя.

        Args:
            telegram_id: 
                Telegram ID пользователя.
            set: 
                Статус. Если True, пользователь - администратор.

        Returns:
            :obj:`bool`: Состояние выполнения функции (False - пользователь не найден).
        '''
        return cls.update_user(telegram_id, is_admin=set)

    @classmethod
    def get_user(cls, telegram_id: int) -> Optional[User]:
        '''Получить пользователя из базы данных по Telegram ID.
        
        Args:
            telegram_id: 
                Telegram ID пользователя.

        Returns:
            :class:`tgbot.database.wrappers.DBUser`: Пользователь из базы (обёртка).
        '''
        if not cls.contains_user(telegram_id):
            return None
        return User(UserModel.get(UserModel.telegram_user_id == telegram_id))
    
    @staticmethod
    def get_users() -> Optional[list[User]]:
        '''Получить всех пользователей из базы данных.

        Attention:
            Обратите внимание, что возвращаемый список занимает много места в памяти, 
            так как там хранятся все пользователи базы, так что лишний раз лучше не 
            использовать эту функцию 
        
        Returns:
            list[:class:`tgbot.database.wrappers.DBUser`]: Список пользователей (в обёртке) из базы.
        '''
        return [User(i) for i in UserModel.select()] or None

    @staticmethod
    def get_admins() -> Optional[list[User]]:
        '''Получить всех администраторов из базы данных.
        
        Returns:
            list[:class:`tgbot.database.wrappers.DBUser`]: Список администраторов (в обёртке) из базы.
        '''
        return [User(i) for i in UserModel.select().where(UserModel.is_admin == True)] or None

    @classmethod
    def get_results_of_user(cls, telegram_id: int) -> Optional[list[Result]]:
        '''Получить все результаты тренировок пользователя по его Telegram ID.
        
        Args:
            telegram_id: 
                Telegram ID пользователя.

        Returns:
            list[:class:`tgbot.database.wrappers.DBResult`]: Список результатов тренировок пользователя (в обёртке) из базы.
        '''
        return [Result(i) for i in cls._get_results_of_user(telegram_id)] or None

    @classmethod
    def delete_results_of_user(cls, telegram_id: int) -> bool:
        '''Удалить результаты тренировок пользователя по его Telegram ID.

        Args:
            telegram_id: 
                Telegram ID пользователя.

        Returns:
            :obj:`bool`: Состояние выполнения функции (False - результаты не найдены).
        '''
        workout_results = cls._get_results_of_user(telegram_id)
        if not workout_results:
            return False
        
        for result in workout_results:
            result.delete_instance()
        return True

    @classmethod
    def delete_user(cls, telegram_id: int) -> bool:
        '''Удалить пользователя и его результаты тренировок из базы данных по его Telegram ID.
        
        Args:
            telegram_id: 
                Telegram ID пользователя.

        Returns:
            :obj:`bool`: Состояние выполнения функции (False - пользователь не найден).
        '''
        cls.delete_results_of_user(telegram_id)
        if not cls.contains_user(telegram_id):
            return False
        for user in UserModel.select().where(UserModel.telegram_user_id == telegram_id):
            user.delete_instance()
        return True
    
    @staticmethod
    def _get_results_of_user(telegram_id: int) -> list[ResultModel]:
        return list(ResultModel.select().where(ResultModel.user == telegram_id))