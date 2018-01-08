import os
from collections import namedtuple
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


@pytest.fixture(scope='session')
def db(data):
    db = get_db()
    db.drop_all()
    db.create_all()

    start_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    end_time = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
    db.insertMentor(data.mentor, data.mentorname, data.mentorid, "Python")
    db.insertShift(data.mentorid, start_time, end_time)

    yield db

    db.close()


@pytest.fixture(scope='session', name='data')
def slack_data(config_setup):
    SlackData = namedtuple('SlackData', 'mentor, mentorname, mentorid, username, userid, channel')
    return SlackData('Bryan Bugyi',
                     'bryan.bugyi',
                     'U86U3G52Q',
                     'bryanbugyi34',
                     'U8LRL4L5R',
                     'DUMMY_CHANNEL')
