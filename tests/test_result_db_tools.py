import unittest
from datetime import datetime

from peewee import SqliteDatabase

from tgbot.database import DBResult, Result
from tgbot.database.models import UserModel, ResultModel


database = SqliteDatabase(':memory:')


class TestResultTools(unittest.TestCase):
    def setUp(self):
        database.bind([UserModel, ResultModel])
        database.connect()
        database.create_tables([UserModel, ResultModel])

    def tearDown(self):
        database.drop_tables([UserModel, ResultModel])
        database.close()

    def test_contains_result_arguments(self):
        DBResult.contains_result(result_id=0)

    def test_contains_result_return(self):
        assert DBResult.contains_result(1) == False

        ResultModel.create(
            user = 0,
            type = 'speed',
            result = 'result of workout',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )
        
        assert DBResult.contains_result(1) == True
        assert DBResult.contains_result(2) == False

        ResultModel.create(
            user = 0,
            type = 'speed',
            result = 'result of workout',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )

        assert DBResult.contains_result(2) == True

    def test_create_result_arguments(self):
        DBResult.create_result(
            telegram_id=0,
            type='speed',
            text='result of workout',
            url='https://youtu.be/jJmHZC9NWMU',
            date=datetime.now(),
            is_accepted=False
        )

    def test_create_result_return(self):
        assert DBResult.create_result(
            telegram_id=0,
            type='speed',
            text='result of workout',
            url='https://youtu.be/jJmHZC9NWMU',
            date=datetime.now(),
            is_accepted=False
        ) == None

    @unittest.expectedFailure
    def test_create_result_exception(self):
        DBResult.create_result(
            telegram_id=0,
            type='random_text_blahblah',
            result='result of workout',
            result_url='https://youtu.be/jJmHZC9NWMU',
            date=datetime.now(),
            is_accepted=False
        )

    def test_create_result_functional(self):
        assert DBResult.create_result(
            telegram_id=0,
            type='speed',
            text='result of workout',
            url='https://youtu.be/jJmHZC9NWMU',
            date=datetime.now(),
            is_accepted=False
        ) == None

        result = ResultModel.select().get()
        assert result.id == 1

        assert DBResult.create_result(
            telegram_id=1,
            type='speed',
            text='result of workout 2',
            url='https://youtu.be/jJmHZC9NWMU'
        ) == None

        result = list(ResultModel.select())
        assert len(result) == 2

        assert result[1].id == 2

    def test_update_result_arguments(self):
        ResultModel.create(
            user = 0,
            type = 'speed',
            result = 'result of workout',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )

        DBResult.update_result(
            result_id=0,
            type='endurance',
            text='result of workout 2',
            url='https://youtu.be/jJmHZC9NWMU',
            date=datetime.now(),
            is_accepted=True
        )
    
    def test_update_result_return(self):
        assert DBResult.update_result(0) == False

        ResultModel.create(
            user = 0,
            type = 'speed',
            result = 'result of workout',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )

        assert DBResult.update_result(1, is_accepted=True) == True

    @unittest.expectedFailure
    def test_update_result_exception(self):
        ResultModel.create(
            user = 0,
            type = 'speed',
            result = 'result of workout',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )

        assert DBResult.update_result(0, is_accepted=True) == True

        DBResult.update_result(
            result_id=0,
            type=None,
            result=None,
            result_url=None,
            date=None,
            is_accepted=None
        )

    def test_update_result_functional(self):
        ResultModel.create(
            user = 0,
            type = 'speed',
            result = 'result of workout',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )

        assert DBResult.update_result(
            result_id=1,
            type='endurance',
            text='result of workout 2',
            url='https://youtu.be/jJmHZC9NWMU',
            date=datetime.now(),
            is_accepted=True
        ) == True

        res = Result(ResultModel.select().get())
        assert res.id == 1
        assert res.user == None
        assert res.type == 'endurance'

        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=False
        )

        assert res.user.telegram_id == 0

    def test_get_result_arguments(self):
        DBResult.get_result(result_id=1)
    
    def test_get_result_return(self):
        assert DBResult.get_result(1) == None

        ResultModel.create(
            user = 0,
            type = 'speed',
            result = 'result of workout',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )

        result = DBResult.get_result(1)
        assert type(result) == Result

    def test_get_result_functional(self):
        ResultModel.create(
            user = 0,
            type = 'speed',
            result = 'result of workout',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )

        result = DBResult.get_result(1)
        assert result.id == 1 #type: ignore
        assert result.type == 'speed' #type: ignore
        assert result.text == 'result of workout' #type: ignore

    def test_delete_result_arguments(self):
        DBResult.delete_result(result_id=1)

    def test_delete_result_return(self):
        assert DBResult.delete_result(1) == False

        ResultModel.create(
            user = 0,
            type = 'speed',
            result = 'result of workout',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )

        assert DBResult.delete_result(1) == True

        assert DBResult.delete_result(1) == False

    def test_delete_result_functional(self):
        assert DBResult.delete_result(1) == False

        ResultModel.create(
            user = 0,
            type = 'speed',
            result = 'result of workout',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )

        assert DBResult.delete_result(1) == True

        results = list(ResultModel.select())
        assert len(results) == 0

        assert DBResult.delete_result(1) == False
