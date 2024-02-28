from datetime import datetime

from peewee import Model, Proxy
from peewee import IntegerField, CharField, BooleanField, DateTimeField, ForeignKeyField, AutoField
from peewee import Check


from tgbot.constants import WORKOUT_TYPES


proxy = Proxy()


class UserModel(Model):
    telegram_user_id = IntegerField()
    first_name = CharField()
    last_name = CharField()
    training_days = IntegerField()
    is_admin = BooleanField()
    register_date = DateTimeField(default=datetime.now)

    class Meta:
        database = proxy
        table_name = 'user'


class ResultModel(Model):
    id = AutoField()
    user = ForeignKeyField(UserModel, field='telegram_user_id')
    type = CharField(constraints=[Check(f'type IN {WORKOUT_TYPES}')])
    result = CharField()
    result_url = CharField()
    date = DateTimeField()
    is_accepted = BooleanField()
    
    class Meta:
        database = proxy
        table_name = 'result'
    

class WorkoutModel(Model):
    id = AutoField()
    name = CharField()
    type = CharField(constraints=[Check(f'type IN {WORKOUT_TYPES}')])
    text = CharField()
    creation_date = DateTimeField(default=datetime.now)
    
    class Meta:
        database = proxy
        table_name = 'workout'
