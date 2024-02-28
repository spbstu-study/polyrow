from tgbot.database.models import UserModel
from tgbot.database.wrappers.dbwrapper import DatabaseWrapper


class User(DatabaseWrapper):
    '''Безопасная обёртка для модели базы данных.

    Класс, оборачивающий UserModel и предотвращающий исключения, возникающие на уровне
    библиотеки для работы с базами данных. Позволяет удобно и безопасно получить
    основную информацию о пользователе.

    Warning:
        Объекты обёртки статичны, а значит не обновляются автоматически после update_user(). 
        Чтобы получить обновлённый объект воспользуйтесь get_user().
    '''
    def __init__(self, model: UserModel) -> None:
        self.__model: UserModel = model

    def __str__(self):
        return f'<user object with id {self.telegram_id}>'
    
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, User):
            return False
        return self.telegram_id == __o.telegram_id

    @property
    def telegram_id(self) -> int:
        '''ID пользователя в Telegram.'''
        return self.__model.telegram_user_id
        
    @property
    def first_name(self) -> str:
        '''Имя пользователя.'''
        return self.__model.first_name
        
    @property
    def last_name(self) -> str:
        '''Фамилия пользователя.'''
        return self.__model.last_name
        
    @property
    def number_training_days(self) -> int:
        '''Количество тренировок в неделю.'''
        return self.__model.training_days
        
    @property
    def is_admin(self) -> bool:
        '''Права пользователя (True - администратор, False - ученик).'''
        return self.__model.is_admin
    
    @property
    def register_date(self) -> bool:
        '''Дата добавления пользователя в базу данных.'''
        return self.__model.register_date
