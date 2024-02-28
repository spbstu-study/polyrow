'''Помогает управлять базой данных

Используйте строки конфига, чтобы управлять настройками
'''
import logging

from peewee import ( # type: ignore
    SqliteDatabase,
)

from tgbot.database.models import ( # type: ignore
    proxy,
    UserModel,
    ResultModel,
    WorkoutModel
)
from config import DATABASE_PATH


# -----------------------------------------------------------
#                           КОНФИГ
# -----------------------------------------------------------
# Изменить режим взаимодействия с базой данных
# Доступно: 
#   RESET (перезаписать все данные), 
#   UPDATE (добавить новые таблицы, старые данные сохраняются)
MODE = 'RESET'
# Путь к базе данных, можно создавать несколько с разными тес
# товыми данными
PATH = DATABASE_PATH
# -----------------------------------------------------------


logging.basicConfig(
    level=logging.INFO
)


LOGGER = logging.getLogger('db-manager')


DATABASE = SqliteDatabase(PATH)
proxy.initialize(DATABASE)


def _create_tables():
    UserModel.create_table()
    ResultModel.create_table()
    WorkoutModel.create_table()


def _drop_tables():
    UserModel.drop_table()
    ResultModel.drop_table()
    WorkoutModel.drop_table()


def update():
    _create_tables()
    LOGGER.info('Database was succesfully updated.')


def reset():
    _drop_tables()
    _create_tables()
    LOGGER.info('Database data resetted succesfully.')


MODES = {
    'UPDATE': update,
    'RESET': reset, 
}


if __name__ != '__main__':
    raise Exception('This module cannot be imported and must be used as main.')


if __name__ == '__main__':
    action = MODES.get(MODE)
    if action is None:
        raise Exception('Chosen mode name is incompatible, change mode in config lines above.')
    else:
        action()
