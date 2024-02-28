import unittest
from datetime import datetime

from peewee import SqliteDatabase

from tgbot.database import DBUser, Result, User
from tgbot.database.models import UserModel, ResultModel


database = SqliteDatabase(':memory:')


class TestUserTools(unittest.TestCase):
    def setUp(self):
        database.bind([UserModel, ResultModel])
        database.connect()
        database.create_tables([UserModel, ResultModel])

    def tearDown(self):
        database.drop_tables([UserModel, ResultModel])
        database.close()

    def test_contains_user_arguments(self):     
        DBUser.contains_user(0)

    def test_contains_user_return(self):
        assert DBUser.contains_user(0) == False

        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=False
        )
        
        assert DBUser.contains_user(0) == True

    def test_contains_user_few_users(self):
        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=False
        )

        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=False
        )

        assert DBUser.contains_user(0) == True

    def test_create_user_arguments(self):
        DBUser.create_user(
            telegram_id=0,
            first_name='Testy',
            last_name='Testman',
            number_training_days=0,
            is_admin=False
        )

    def test_create_user_return(self):
        assert DBUser.create_user(
            telegram_id=0,
            first_name='Testy',
            last_name='Testman',
            number_training_days=0,
            is_admin=False
        ) == None


    @unittest.expectedFailure
    def test_create_user_exception(self):
        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=False
        )

        DBUser.create_user(
            telegram_id=0,
            first_name='Testy',
            last_name='Testman',
            number_training_days=0
        )
    
    def test_create_user_functional(self):
        DBUser.create_user(
            telegram_id=0,
            first_name='Testy',
            last_name='Testman',
            number_training_days=0
        )

        user = UserModel.select().get()
        assert user.telegram_user_id == 0

    def test_update_user_arguments(self):
        DBUser.update_user(
            telegram_id=0,
            first_name=None,
            last_name=None,
            number_training_days=None,
            is_admin=None
        )

    def test_update_user_return(self):
        assert DBUser.update_user(0) == False

        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=False
        )

        assert DBUser.update_user(0, is_admin=True) == True

    @unittest.expectedFailure
    def test_update_user_exception(self):
        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=False
        )

        assert DBUser.update_user(0, is_admin=True) == True

        DBUser.update_user(
            telegram_id=0,
            first_name=None,
            last_name=None,
            number_training_days=None,
            is_admin=None
        )

    def test_update_user_functional(self):
        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=False
        )

        assert DBUser.update_user(
            telegram_id=0,
            first_name='Not Testy',
            last_name='Not Testman',
            number_training_days=1,
            is_admin=True
        ) == True

        user = UserModel.select().get()
        assert user.telegram_user_id == 0
        assert user.first_name == 'Not Testy'
        assert user.last_name == 'Not Testman'
        assert user.training_days == 1
        assert user.is_admin == True

    def test_set_admin_arguments(self):
        DBUser.set_admin(telegram_id=0, set=True)

    def test_set_admin_return(self):
        assert DBUser.set_admin(telegram_id=0, set=True) == False

        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=False
        )

        assert DBUser.set_admin(telegram_id=0, set=True) == True

    def test_set_admin_functional(self):
        assert DBUser.set_admin(telegram_id=0, set=True) == False

        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=False
        )

        assert DBUser.set_admin(telegram_id=0, set=True) == True

        user = UserModel.select().get()
        assert user.is_admin == True

    def test_get_user_arguments(self):
        DBUser.get_user(telegram_id=0)

    def test_get_user_return(self):
        assert DBUser.get_user(0) == None

        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=False
        )

        user = DBUser.get_user(0)
        assert type(user) == User

    def test_get_user_functional(self):
        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=False
        )

        user = DBUser.get_user(0)
        assert user.telegram_id == 0 # type: ignore
        assert user.first_name == 'Testy' # type: ignore
        assert user.last_name == 'Testman' # type: ignore
        assert user.number_training_days == 0 # type: ignore
        assert user.is_admin  == False # type: ignore

    def test_get_users_return(self):
        assert DBUser.get_users() == None

        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=False
        )

        assert type(DBUser.get_users()) == list

        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=False
        )

        assert type(DBUser.get_users()) == list

        users = DBUser.get_users()
        if users:
            for i in users:
                assert type(i) == User

    def test_get_users_functional(self):
        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=False
        )
        UserModel.create(
            telegram_user_id=1, 
            first_name='Testina',
            last_name='Testman',
            training_days=8,
            is_admin=True
        )

        users = DBUser.get_users()
        assert users is not None
        assert len(users) == 2
        first = users[0]
        second = users[1]

        assert first.telegram_id == 0
        assert second.telegram_id == 1

    def test_get_admins_return(self):
        assert DBUser.get_admins() == None

        UserModel.create(
            telegram_user_id=1, 
            first_name='Testina',
            last_name='Testman',
            training_days=8,
            is_admin=True
        )

        assert type(DBUser.get_admins()) == list

        admins = DBUser.get_admins()
        if admins:
            for i in admins:
                assert type(i) == User

    def test_get_admins_functional(self):
        UserModel.create(
            telegram_user_id=1, 
            first_name='Testina',
            last_name='Testman',
            training_days=8,
            is_admin=False
        )

        assert DBUser.get_admins() == None

        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=True
        )

        assert type(DBUser.get_admins()) == list

        admins = DBUser.get_admins()

        admin = admins[0] # type: ignore
        assert admin.telegram_id == 0

    def test_get_results_of_user_arguments(self):
        DBUser.get_results_of_user(telegram_id=0)

    def test_get_results_of_user_return(self):
        assert DBUser.get_results_of_user(0) == None

        ResultModel.create(
            user = 0,
            type = 'speed',
            result = 'result of workout',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )

        ResultModel.create(
            user = 0,
            type = 'endurance',
            result = 'result of workout 2',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )

        assert type(DBUser.get_results_of_user(0)) == list 

        results = DBUser.get_results_of_user(0)
        if results:
            for i in results:
                assert type(i) == Result
    
    def test_get_results_of_user_functional(self):
        assert DBUser.get_results_of_user(0) == None

        ResultModel.create(
            user = 0,
            type = 'speed',
            result = 'result of workout',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )

        ResultModel.create(
            user = 0,
            type = 'endurance',
            result = 'result of workout 2',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )

        results = DBUser.get_results_of_user(0)
        assert len(results) == 2 # type: ignore
        first = results[0] # type: ignore
        second = results[1] # type: ignore
        assert first.id == 1
        assert second.id == 2

        del results, first, second

        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=True
        )

        results = DBUser.get_results_of_user(0)
        assert len(results) == 2 #type: ignore
        first = results[0] #type: ignore
        second = results[1] #type: ignore
        assert first.id == 1 #type: ignore
        assert second.id == 2

    def test_delete_results_of_user_arguments(self):
        DBUser.delete_results_of_user(telegram_id=0)

    def test_delete_results_of_user_return(self):
        assert DBUser.delete_results_of_user(telegram_id=0) == False

        ResultModel.create(
            user = 0,
            type = 'speed',
            result = 'result of workout',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )

        assert DBUser.delete_results_of_user(telegram_id=0) == True

        assert DBUser.delete_results_of_user(telegram_id=0) == False

    def test_delete_results_of_user_functional(self):
        assert DBUser.delete_results_of_user(telegram_id=0) == False

        ResultModel.create(
            user = 0,
            type = 'speed',
            result = 'result of workout',
            result_url = 'https://youtu.be/dQw4w9WgXcQ',
            date=datetime.now(),
            is_accepted=False
        )

        assert DBUser.delete_results_of_user(telegram_id=0) == True

        results = list(ResultModel.select().where(ResultModel.user == 0))
        assert len(results) == 0

        for i in range(2):
            ResultModel.create(
                user = 0,
                type = 'speed',
                result = 'result of workout',
                result_url = 'https://youtu.be/dQw4w9WgXcQ',
                date=datetime.now(),
                is_accepted=False
            )

        assert DBUser.delete_results_of_user(telegram_id=0) == True

        results = list(ResultModel.select().where(ResultModel.user == 0))
        assert len(results) == 0

        for i in range(10):
            ResultModel.create(
                user = 0,
                type = 'speed',
                result = 'result of workout',
                result_url = 'https://youtu.be/dQw4w9WgXcQ',
                date=datetime.now(),
                is_accepted=False
            )

        assert DBUser.delete_results_of_user(telegram_id=0) == True

        results = list(ResultModel.select().where(ResultModel.user == 0))
        assert len(results) == 0

        assert DBUser.delete_results_of_user(telegram_id=0) == False

    def test_delete_user_arguments(self):
        DBUser.delete_user(telegram_id=0)

    def test_delete_user_return(self):
        assert DBUser.delete_user(0) == False

        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=True
        )

        assert DBUser.delete_user(0) == True

        assert DBUser.delete_user(0) == False

    def test_delete_user_functional(self):
        assert DBUser.delete_user(0) == False

        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=True
        )

        assert DBUser.delete_user(0) == True

        users = list(UserModel.select())
        results = list(ResultModel.select().where(ResultModel.user == 0))
        assert len(users) == 0
        assert len(results) == 0

        UserModel.create(
            telegram_user_id=0, 
            first_name='Testy',
            last_name='Testman',
            training_days=0,
            is_admin=True
        )

        for i in range(10):
            ResultModel.create(
                user = 0,
                type = 'speed',
                result = 'result of workout',
                result_url = 'https://youtu.be/dQw4w9WgXcQ',
                date=datetime.now(),
                is_accepted=False
            )
        
        assert DBUser.delete_user(0) == True

        users = list(UserModel.select())
        results = list(ResultModel.select().where(ResultModel.user == 0))
        assert len(users) == 0
        assert len(results) == 0

        assert DBUser.delete_user(0) == False

    def test_all_user_tools(self):
        assert DBUser.contains_user(0) == False

        assert DBUser.get_users() == None

        assert DBUser.update_user(0) == False

        assert DBUser.create_user(
            telegram_id=0,
            first_name='Testy',
            last_name='Testman',
            number_training_days=0,
            is_admin=False
        ) == None

        assert DBUser.contains_user(0) == True

        with self.assertRaises(Exception):
            DBUser.create_user(
                telegram_id=0,
                first_name='Testy',
                last_name='Testman',
                number_training_days=0,
                is_admin=False
            )
        
        assert DBUser.create_user(
            telegram_id=1,
            first_name='Testina',
            last_name='Testman',
            number_training_days=7,
            is_admin=True
        ) == None

        assert DBUser.contains_user(1) == True

        with self.assertRaises(ValueError):
            DBUser.update_user(0)

        assert DBUser.update_user(0, 'Not Testy', is_admin=True) == True

        user = DBUser.get_user(0)
        assert user.first_name == 'Not Testy' # type: ignore
        assert user.is_admin == True # type: ignore
        assert user.last_name == 'Testman' # type: ignore
        assert user.number_training_days == 0 # type: ignore

        user = DBUser.get_user(2)

        assert user == None

        assert DBUser.set_admin(0, set=False) == True

        user = DBUser.get_user(0)
        assert user.is_admin == False # type: ignore

        assert DBUser.update_user(2, 'Not Testy', is_admin=True) == False

        list_users = [DBUser.get_user(0), DBUser.get_user(1)]
        users = DBUser.get_users()
        for i, user in enumerate(users): # type: ignore
            assert user == list_users[i]

        admins = DBUser.get_admins()

        user_0 = DBUser.get_user(0)
        user_1 = DBUser.get_user(1)
        assert len(admins) == 1 # type: ignore
        assert bool(user_0 in admins) == False # type: ignore
        assert bool(user_1 in admins) == True # type: ignore
