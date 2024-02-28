from datetime import datetime
from typing import Optional

from peewee import DoesNotExist

from tgbot.database.models import WorkoutModel
from tgbot.database.wrappers.workout import Workout
from tgbot.database.decorators import check_type_exception
from tgbot.database.api.dbobj import DBObject
from tgbot.constants import WORKOUT_TYPES


class DBWorkout(DBObject):
    '''Предоставляет методы для работы с тренировками в базе данных.'''
    @staticmethod
    def contains_workout(workout_id: int) -> bool:
        '''Проверить, есть ли в базе данных тренировка с заданным id.

        Args:
            workout_id (int): ID тренировки в базе данных.

        Returns:
            bool: Состояние нахождения в базе данных.
        '''
        try:
            WorkoutModel.get(WorkoutModel.id == workout_id)
            return True
        except DoesNotExist:
            return False
    
    @staticmethod
    @check_type_exception
    def create_workout(type: str, name: str, text: str, creation_date: datetime = datetime.now()) -> None:      
        '''Создать и добавить тренировку в базу данных.

        Создаёт тренировку в базе, используя такие же параметры, как в обёртке.

        Args:
            type (str): Один из доступных типов тренировок.
            name (str): Заголовок тренировки.
            text (str): Текст-заполнение тренировки.
            creation_date (datetime, optional): Дата создания тренировки. По умолчанию datetime.now().
        '''
        WorkoutModel.create(
            type=type,
            name=name,
            text=text,
            creation_date=creation_date
        )

    @staticmethod
    def get_workouts(type: str = 'all') -> Optional[list[Workout]]:
        '''Получить тренировки заданного типа.

        Даёт возможность получить либо все тренировки из базы (по умолчанию), либо
        определённого типа.

        Args:
            type (str, optional): Тип тренировки. По умолчанию 'all'.

        Raises:
            Exception: 'The value of the `type` argument does not match any of the following types: {WORKOUT_TYPES}.'

        Returns:
            Optional[list[Workout]]: Список тренировок.
        '''
        if type == 'all':
            return [Workout(i) for i in WorkoutModel.select()] or None

        if not type in WORKOUT_TYPES:
            raise Exception(f'The value of the `type` argument does not match any of the following types: {WORKOUT_TYPES}.')
        
        return [Workout(i) for i in WorkoutModel.select().where(WorkoutModel.type == type)] or None

    @classmethod
    def get_workout(cls, workout_id: int) -> Optional[Workout]:
        '''Получить тренировку по её ID в базе.

        Args:
            workout_id (int): ID тренировки в базе данных.

        Returns:
            Optional[Workout]: Представление тренировки.
        '''
        if not cls.contains_workout(workout_id):
            return None

        return Workout(WorkoutModel.get(WorkoutModel.id == workout_id))

    @classmethod
    def delete_workout(cls, workout_id: int) -> bool:
        '''Удалить тренировку по её ID в базе.

        Args:
            workout_id (int): ID тренировки в базе данных.

        Returns:
            bool: Состояние выполнения функции (False - удаление не было завершено).
        '''
        if not cls.contains_workout(workout_id):
            return False
        
        for result in WorkoutModel.select().where(WorkoutModel.id == workout_id):
            result.delete_instance()

        return True