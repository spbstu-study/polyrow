from datetime import datetime

from tgbot.database.models import WorkoutModel
from tgbot.database.wrappers.dbwrapper import DatabaseWrapper


class Workout(DatabaseWrapper):
    '''Безопасная обёртка для модели базы данных.

    Класс, оборачивающий WorkoutModel и предотвращающий исключения, возникающие на уровне
    библиотеки для работы с базами данных. Позволяет удобно и безопасно получить
    основную информацию о результате тренировки.
    '''
    def __init__(self, model: WorkoutModel) -> None:
        self.__model: WorkoutModel = model
    
    def __str__(self):
        return f'<workout object \"{self.id}\">'
    
    @property
    def id(self) -> int:
        return self.__model.id

    @property
    def name(self) -> str:
        return self.__model.name
    
    @property
    def type(self) -> str:
        return self.__model.type
    
    @property
    def text(self) -> str:
        return self.__model.text

    @property
    def creation_date(self) -> datetime:
        return self.__model.creation_date
