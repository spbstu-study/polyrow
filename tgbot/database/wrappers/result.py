from datetime import datetime

from peewee import DoesNotExist

from tgbot.database.models import ResultModel
from tgbot.database.wrappers.user import User
from tgbot.database.wrappers.dbwrapper import DatabaseWrapper


class Result(DatabaseWrapper):
    '''Безопасная обёртка для модели базы данных.

    Класс, оборачивающий ResultModel и предотвращающий исключения, возникающие на уровне
    библиотеки для работы с базами данных. Позволяет удобно и безопасно получить
    основную информацию о результате тренировки.

    .. warning::
        Объекты обёртки статичны, а значит не обновляются автоматически после update_result().
        Чтобы получить обновлённый объект воспользуйтесь get_result().
    '''
    def __init__(self, model: ResultModel) -> None:
        self.__model: ResultModel = model

    def __str__(self):
        return f'<workout result object \"{self.id}\" of {self.user} user>'
    
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Result):
            return False
        return self.id == __o.id
    
    @property
    def id(self) -> int:
        '''Индивидуальный ID результата в базе данных.'''
        return self.__model.id
    
    @property
    def user(self) -> User:
        '''ID пользователя в Telegram, которому принадлежит результат тренировки.'''
        try:
            return User(self.__model.user)
        except DoesNotExist:
            return None

    @property
    def type(self) -> str:
        '''Один из типов тренировок.'''
        return self.__model.type

    @property
    def text(self) -> str:
        '''Результат тренировки в текстовом формате.'''
        return self.__model.result

    @property
    def url(self) -> str:
        '''Ссылка на результат тренировки.'''
        return self.__model.result_url

    @property
    def date(self) -> datetime:
        '''Дата выполнения тренировки.'''
        return self.__model.date

    @property
    def is_accepted(self) -> bool:
        '''Состояние одобрения администратором (False - не принята, True - принята).'''
        return self.__model.is_accepted
