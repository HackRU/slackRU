""" Shared Testing Utilities """

import os
import inspect
from datetime import datetime, timedelta

import flask
from flask_testing import TestCase

from slackru import get_db


def params(*parameters):
    """ Example Usage:

            @params((1,2,3), (2,4,6), (5,6,11))
            def test_add(x, y, z):
                self.assertEqual(add(x, y), z)

        The above example will run 3 tests total: one where x=1, y=2, z=3; one where x=2, y=4, z=6;
        and one where x=5, y=6, z=11.
    """
    def decorator(func):
        def newTest(self):
            for args in parameters:
                with self.subTest(**dict(zip(inspect.getfullargspec(func).args[1:], args))):
                    func(self, *args)
        return newTest
    return decorator


class TestBase(TestCase):
    """ Base Unit Testing Class. Inherited by all other test classes. """
    hasRunSetup = False  # Used to enforce SESSION setup instead of CLASS setup

    @classmethod
    def setUpClass(cls):
        if not cls.hasRunSetup:
            os.environ['SLACK_CONFIG'] = 'development'
            from slackru.config import config
            flask.testing = True
            config.setup()

            cls.db = get_db()
            cls.db.drop_all()
            cls.db.create_all()

            cls.data = dict()
            cls.data['mentor'] = ['Bryan Bugyi', 'Timmy Tester']
            cls.data['mentorname'] = ['bryan.bugyi', 'tester.timmy']
            cls.data['mentorid'] = ['U86U3G52Q', 'U8R4CCDV4']
            cls.data['username'] = 'bryanbugyi34'
            cls.data['userid'] = 'U8LRL4L5R'
            cls.data['channel'] = ['D86QQ6P2P', 'D8RAAMGJ3']
            cls.data['question'] = ['I am having some trouble with my Python code.', 'I love JAVA', 'I hate C++!']

            start_time = datetime.now().strftime('%Y-%m-%d %H:%M')
            end_time = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
            cls.db.insertMentor(cls.data['mentor'][0], cls.data['mentorname'][0], cls.data['mentorid'][0], "Python")
            cls.db.insertMentor(cls.data['mentor'][1], cls.data['mentorname'][1], cls.data['mentorid'][1], "Java")
            cls.db.insertShift(cls.data['mentorid'][0], start_time, end_time)
            cls.db.insertShift(cls.data['mentorid'][1], start_time, end_time)

            cls.hasRunSetup = True

    def create_app(self):
        """ Used by Flask-Testing package to create app context """
        from slackru import create_app
        app = create_app()
        app.config['TESTING'] = True
        return app
