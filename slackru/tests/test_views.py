import unittest
import json
from datetime import datetime, timedelta

from slackru.tests.test_base import TestBase


class TestViews(TestBase):
    @classmethod
    def setUpClass(cls):
        TestBase.setUpClass()

        from slackru import create_app
        cls.app = create_app()

        cls.db = cls.app.db.get()
        cls.db.drop_all()
        cls.db.create_all()

        cls.pythonQuestion = "I need help with Python. Something's not working the way it should."

        start_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        end_time = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
        cls.db.insertMentor(cls.mentor, cls.mentorname, cls.mentorid, "Python")
        cls.db.insertShift(cls.mentorid, start_time, end_time)

    @classmethod
    def tearDownClass(cls):
        TestBase.tearDownClass()
        cls.db.close()

    def setUp(self):
        self.db.drop_table('questions')
        self.db.create_questions()


class TestPairMentor(TestViews):
    def send_request(self, question):
        postData = {'question': question,
                    'username': self.username,
                    'userid': self.userid}

        with self.app.test_client() as client:
            resp = client.post(self.config.serverurl + 'pairmentor', data=postData)
            self.assertEqual(200, resp.status_code)

    def test_match(self):
        self.send_request(self.pythonQuestion)

    def test_no_match(self):
        self.send_request("What is 2+2?")


class TestMessageAction(TestViews):
    def setUp(self):
        TestViews.setUp(self)
        self.db.insertQuestion(self.pythonQuestion, self.username, self.userid, json.dumps([self.userid]))

    def send_request(self, value, callback):
        payload = {"actions": [{"name": "answer",
                                "value": value,
                                "type": "button"}],
                   "callback_id": callback,
                   "user": {'id': self.mentorid,
                            'name': self.mentorname},
                   'message_ts': '111111111111',
                   'channel': {'id': 'D86QQ6P2P',
                               'name': 'general'}}
        postData = {'payload': json.dumps(payload)}
        with self.app.test_client() as client:
            resp = client.post(self.config.serverurl + 'message_action', data=postData)
            self.assertEqual(200, resp.status_code)

    def test_accept(self):
        self.send_request("yes", "mentorResponse_1")

    def test_decline(self):
        self.send_request("no", "mentorResponse_1")

    def test_invalid_callback(self):
        self.send_request("yes", "INVALID")


if __name__ == '__main__':
    unittest.main()
