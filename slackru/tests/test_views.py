import os
import unittest
import flask
import json
from datetime import datetime, timedelta


class TestViews(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['SLACK_CONFIG'] = 'development'
        flask.testing = True

        from slackru.config import config
        from slackru import create_app

        config.setup()

        if os.path.isfile(config.dbpath):
            os.remove(config.dbpath)
        app = create_app(config)
        db = app.db.get_db()

        cls.user = "Bryan Bugyi"
        cls.username = "bryan.bugyi"
        cls.userid = "U86U3G52Q"
        db.insertMentor(cls.user, cls.username, cls.userid, "Python")

        start = datetime.now().strftime('%Y-%m-%d %H:%M')
        end = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
        db.insertShift(cls.userid, start, end)

        cls.db = db
        cls.app = app
        cls.config = config

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_pairMentor(self):
        postData = {'question': 'I need help with Python',
                    'username': self.username,
                    'userid': self.userid}

        with self.app.test_client() as client:
            resp = client.post(self.config.serverurl + 'pairmentor', data=postData)
            self.assertEqual(json.loads(resp.data), [self.userid])


if __name__ == '__main__':
    unittest.main()
