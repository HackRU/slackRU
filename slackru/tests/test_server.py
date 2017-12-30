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

        cls.user = "Bryan Bugyi"
        cls.username = "bryan.bugyi"
        cls.userid = "U86U3G52Q"
        db.insertMentor(cls.user, cls.username, cls.userid, "Python")

        start = datetime.now().strftime('%Y-%m-%d %H:%M')
        end = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
        db.insertShift(cls.userid, start, end)

        cls.questionId = db.insertQuestion("Test Question", cls.username, cls.userid, json.dumps([cls.userid]))

        cls.db = db
        cls.app = app
        cls.config = config

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_query_db(self):
        query = self.db.query_db("SELECT * FROM mentors", one=True)
        self.assertEqual(query['name'], self.user)
        self.assertEqual(query['keywords'], "Python")

    def test_pairMentor(self):
        postData = {'question': 'I need help with Python',
                    'username': self.username,
                    'userid': self.userid}

        with self.app.test_client() as client:
            resp = client.post(self.config.serverurl + 'pairmentor', data=postData)
            self.assertEqual(json.loads(resp.data), [self.userid])

    def test_askQuestion(self):
        from slackru.serverside import askQuestion
        askQuestion(self.db, "What is 2+2?", self.username, self.userid)

        actual = [val for val in self.db.query_db("SELECT question,answered,username,userid,matchedMentors,assignedMentor FROM questions WHERE question='What is 2+2?'", one=True).values()]
        expected = ["What is 2+2?", 0, self.username, self.userid,
                    '["{0}"]'.format(self.userid), None]

        self.assertEqual(expected, actual)

    def test_answerQuestion(self):
        with self.app.test_client() as client:
            client.get(self.config.serverurl + 'answer/' + self.userid + '/' + str(self.questionId))
            expected = ["Test Question", 1, self.username, self.userid,
                        '["{0}"]'.format(self.userid), self.userid]

            actual = [val for val in self.db.query_db("SELECT question,answered,username,userid,matchedMentors,assignedMentor FROM questions WHERE question='Test Question'", one=True).values()]

            self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
