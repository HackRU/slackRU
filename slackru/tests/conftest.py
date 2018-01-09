import os
from datetime import datetime, timedelta

import pytest
import flask

from slackru import create_app, get_db


@pytest.fixture
def app():
    os.environ['SLACK_CONFIG'] = 'development'
    app = create_app()
    return app


@pytest.fixture(scope='session')
def config_setup():
    from slackru.config import config
    flask.testing = True
    config.setup()


@pytest.fixture(scope='module')
def db(data):
    db = get_db()
    db.drop_all()
    db.create_all()

    start_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    end_time = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
    db.insertMentor(data['mentor'][0], data['mentorname'][0], data['mentorid'][0], "Python")
    db.insertMentor(data['mentor'][1], data['mentorname'][1], data['mentorid'][1], "Java")
    db.insertShift(data['mentorid'][0], start_time, end_time)
    db.insertShift(data['mentorid'][1], start_time, end_time)

    yield db

    db.close()


@pytest.fixture(scope='session')
def data(config_setup):
    data = dict()
    data['mentor'] = ['Bryan Bugyi', 'Timmy Tester']
    data['mentorname'] = ['bryan.bugyi', 'tester.timmy']
    data['mentorid'] = ['U86U3G52Q', 'U8R4CCDV4']
    data['username'] = 'bryanbugyi34'
    data['userid'] = 'U8LRL4L5R'
    data['channel'] = ['D86QQ6P2P', 'D8RAAMGJ3']
    data['question'] = ['I am having some trouble with my Python code.', 'I love JAVA', 'I hate C++!']

    return data
