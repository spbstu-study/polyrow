from datetime import datetime
from typing import Optional

from peewee import DoesNotExist

from tgbot.database.models import ResultModel
from tgbot.database.wrappers.result import Result
from tgbot.database.decorators import check_type_exception
from tgbot.database.api.dbobj import DBObject


class DBResult(DBObject):
    '''Предоставляет методы для работы с результатами тренировки в базе данных'''
    @staticmethod
    def contains_result(result_id: int) -> bool:
        '''Проверить, есть ли в базе данных результат тренировки с заданным ID.
        
        Args:
            result_id: 
                Индивидуальный ID результата в базе данных.

        Returns:
            :obj:`bool`: Состояние нахождения в базе данных.
        '''
        try:
            ResultModel.get(ResultModel.id == result_id)
            return True
        except DoesNotExist:
            return False
        
    @staticmethod
    @check_type_exception
    def create_result(telegram_id: int, type: str, text: str, url: str, date: datetime = datetime.now(), is_accepted: bool = False) -> None:
        '''Создать и добавить результат тренировки в базу данных.
        
        Создаёт результат тренировки в базе, используя такие же параметры, как в обёртке :class:`tgbot.database.wrappers.DBResult`.
        Результату автоматически присваевается его индивидуальный ID.
        .. attention::
            Тип тренировок должен быть одним из данного списка: ['Полина, когда ты уже список тренировок сделаешь, блин?'].

        Args:
            telegram_id:
                Telegram ID пользователя, которому принадлежит результат.
            type:
                Один из типов тренировок.        
            text:
                Текстовый результат тренировки.
            url:
                Ссылка на результат тренировки.
            date:
                Дата выполнения тренировки.
            is_accepted:
                Состояние одобрения администратором (False - не принята, True - принята).

        Raises:
            Exception: The value of the `result` argument does not match any of the following types: {WORKOUT_TYPES}.
        '''
        ResultModel.create(
            user=telegram_id, 
            date=date,
            type=type,
            result=text,
            result_url=url,
            is_accepted=is_accepted
        )

    @classmethod
    @check_type_exception
    def update_result(cls, result_id: int, telegram_id: Optional[int] = None, type: Optional[str] = None, 
                    text: Optional[str] = None, url: Optional[str] = None, 
                    date: Optional[datetime] = None, is_accepted: Optional[bool] = None) -> bool:
        '''Обновить результат тренировки в базе данных.
        
        Обновляет результат в базе по его индивидуальному ID, используя параметры, как и в обёртке :class:`tgbot.database.wrappers.DBResult`.
        .. attention::
            Тип тренировок должен быть одним из данного списка: ['Полина, когда ты уже список тренировок сделаешь, блин?'].

        Args:
            result_id:
                Индивидуальный ID результата тренировки.
            telegram_id:
                Telegram ID пользователя, которому принадлежит результат.
            type:
                Один из типов тренировок.        
            text:
                Текстовый результат тренировки.
            url:
                Ссылка на результат тренировки.
            date:
                Дата выполнения тренировки.
            is_accepted:
                Состояние одобрения администратором (False - не принята, True - принята).

        Returns:
            :obj:`bool`: Состояние выполнения функции (False - результат не найден). 

        Raises:
            Exception: The value of the `result` argument does not match any of the following types: {WORKOUT_TYPES}.
        '''
        if not cls.contains_result(result_id):
            return False

        params = {
            'user': telegram_id,
            'date': date,
            'type': type,
            'result': text,
            'result_url': url,
            'is_accepted': is_accepted
        }

        params = {k: v for k, v in params.items() if v is not None}

        if not params:
            raise Exception('No argument was passed to the function, at least one is required')

        query = ResultModel.update(params).where(ResultModel.id == result_id)
        query.execute()
        
        return True

    @classmethod
    def get_result(cls, result_id: int) -> Optional[Result]:
        '''Получить результат тренировки из базы данных по его ID.
        
        Args:
            result_id: 
                Индивидуальный ID результата.

        Returns:
            :class:`tgbot.database.wrappers.DBResult`: Результат тренировки из базы (обёртка).
        '''
        if not cls.contains_result(result_id):
            return None

        return Result(ResultModel.get(ResultModel.id == result_id))

    @classmethod
    def delete_result(cls, result_id: int) -> bool:
        '''Удалить результат тренировки из базы данных по ID.
        
        Args:
            result_id: 
                Индивидуальный ID результата.

        Returns:
            :obj:`bool`: Состояние выполнения функции (False - результат не найден).
        
        '''
        if not cls.contains_result(result_id):
            return False
        
        for result in ResultModel.select().where(ResultModel.id == result_id):
            result.delete_instance()

        return True
