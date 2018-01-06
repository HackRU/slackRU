import os
import unittest

import flask


class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['SLACK_CONFIG'] = 'development'

        from slackru.config import config
        cls.config = config
        flask.testing = cls.config.testing = True
        config.setup()

        cls.mentor = "Bryan Bugyi"
        cls.mentorname = "bryan.bugyi"
        cls.mentorid = "U86U3G52Q"

        cls.username = "bryanbugyi34"
        cls.userid = "U8LRL4L5R"

        cls.channel = 'DUMMY_CHANNEL'

    @classmethod
    def tearDownClass(cls):
        pass
