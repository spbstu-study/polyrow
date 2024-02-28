from peewee import IntegrityError

from tgbot.database.models import WORKOUT_TYPES


def check_type_exception(function):
    def execute(*args, **kwars):
        try:
            return function(*args, **kwars)
        except IntegrityError:
            raise Exception(f'The value of the `result` argument does not match any of the following types: {WORKOUT_TYPES}.')
    return execute