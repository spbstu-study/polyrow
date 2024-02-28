import unittest
from datetime import datetime

from peewee import SqliteDatabase

from tgbot.database import DBWorkout, Workout
from tgbot.database.models import UserModel, ResultModel, WorkoutModel
from config import WORKOUT_TYPES


database = SqliteDatabase(':memory:')


class TestUserTools(unittest.TestCase):
    def setUp(self):
        database.bind([UserModel, ResultModel, WorkoutModel])
        database.connect()
        database.create_tables([UserModel, ResultModel, WorkoutModel])

    def tearDown(self):
        database.drop_tables([UserModel, ResultModel, WorkoutModel])
        database.close()

    def test_get_workouts_arguments(self):
        DBWorkout.get_workouts()

        for i in WORKOUT_TYPES:
            DBWorkout.get_workouts(i)
        
    def test_get_workouts_return(self):
        assert DBWorkout.get_workouts() == None

        WorkoutModel.create(
            type='test_type_1',
            name='name',
            text='text',
            creation_date=datetime.now()
        )

        assert type(DBWorkout.get_workouts()) == list

        WorkoutModel.create(
            type='test_type_1',
            name='name',
            text='text',
            creation_date=datetime.now()
        )

        assert type(DBWorkout.get_workouts()) == list

        users = DBWorkout.get_workouts()
        if users:
            for i in users:
                assert type(i) == Workout

    @unittest.expectedFailure
    def test_get_workouts_exception(self):
        DBWorkout.get_workouts('random_type_blah_blah')

    def test_get_workouts_functional(self):
        assert DBWorkout.get_workouts() == None

        assert DBWorkout.get_workouts('all') == None

        assert DBWorkout.get_workouts('test_type_2') == None

        WorkoutModel.create(
            type='test_type_2',
            name='name',
            text='text',
            creation_date=datetime.now()
        )

        WorkoutModel.create(
            type='test_type_1',
            name='name',
            text='text',
            creation_date=datetime.now()
        )

        workouts = DBWorkout.get_workouts('all')

        assert workouts is not None
        assert len(workouts) == 2

        workouts = DBWorkout.get_workouts('test_type_2')
        assert workouts is not None
        assert len(workouts) == 1
