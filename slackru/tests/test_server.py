import os
import unittest
import flask
import json
from datetime import datetime, timedelta


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['SLACK_CONFIG'] = 'testing'
        flask.testing = True

        from slackru.config import config
        from slackru import create_app

        if os.path.isfile(config.dbpath):
            os.remove(config.dbpath)
        app = create_app(config)
        db = app.db.get_db()

        mentor_id = db.insertMentor("Bryan Bugyi", "bryan.bugyi", "U86U3G52Q", "Python")

        start = datetime.now().strftime('%Y-%m-%d %H:%M')
        end = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
        db.insertShift(mentor_id, start, end)

        cls.db = db
        cls.app = app
        cls.config = config

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_query_db(self):
        query = self.db.query_db("SELECT * FROM mentors", one=True)
        self.assertEqual(query['name'], "Bryan Bugyi")
        self.assertEqual(query['keywords'], "Python")
        self.assertEqual(query['id'], 1)

    def test_pairMentor(self):
        postData = {'question': 'I need help with Python',
                    'username': 'bryan.bugyi',
                    'userid': 'U86U3G52Q'}

        with self.app.test_client() as client:
            resp = client.post(self.config.serverurl + 'pairmentor', data=postData)
            self.assertEqual(json.loads(resp.data), ['U86U3G52Q'])

    def test_askQuestion(self):
        from slackru.serverside import askQuestion
        askQuestion(self.db, "What is 2+2?", "bryan.bugyi", "U86U3G52Q")

        actual = [val for val in self.db.query_db("SELECT * FROM questions WHERE question='What is 2+2?'", one=True).values()]
        expected = [1, "What is 2+2?", 0, "bryan.bugyi", "U86U3G52Q",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '["U86U3G52Q"]', None]

        self.assertEqual(expected, actual)

    def test_answerQuestion(self):
        pass


if __name__ == '__main__':
    unittest.main()
