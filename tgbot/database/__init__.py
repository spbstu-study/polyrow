'''Предоставляет API для работы с базой данных'''
import peewee

from tgbot.database.api.result import DBResult
from tgbot.database.api.user import DBUser
from tgbot.database.api.workout import DBWorkout
from tgbot.database.wrappers.result import Result
from tgbot.database.wrappers.user import User
from tgbot.database.wrappers.workout import Workout
from tgbot.database.models import proxy

import config


DATABASE = peewee.SqliteDatabase(config.DATABASE_PATH)
proxy.initialize(DATABASE)
