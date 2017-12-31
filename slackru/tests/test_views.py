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
        db = app.db.open()

        cls.user = "Bryan Bugyi"
        cls.username = "bryan.bugyi"
        cls.userid = "U86U3G52Q"
        db.insertMentor(cls.user, cls.username, cls.userid, "Python")

        start = datetime.now().strftime('%Y-%m-%d %H:%M')
        end = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
        db.insertShift(cls.userid, start, end)

        db.insertQuestion("Who are you?", cls.username, cls.userid, '[{}]'.format(cls.userid))

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
            self.assertEqual("200 OK", resp.status)

    def test_message_action(self):
        payload = {"actions": [{"name": "answer",
                                "value": "no",
                                "type": "button"}],
                   "callback_id": "mentorResponse_1",
                   "user": {'id': self.userid,
                            'name': self.username},
                   'message_ts': '111111111111',
                   'channel': {'id': 'ABCDEFG',
                               'name': 'general'}}

        postData = {'payload': json.dumps(payload)}

        with self.app.test_client() as client:
            resp = client.post(self.config.serverurl + 'message_action', data=postData)
            self.assertNotEqual(b'done', resp.data)
            self.assertEqual("200 OK", resp.status)


if __name__ == '__main__':
    unittest.main()
