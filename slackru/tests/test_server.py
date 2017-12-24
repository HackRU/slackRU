import os
import unittest
import flask
import json


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from slackru.config import getConfig
        from slackru import create_app

        flask.testing = True
        config = getConfig['testing']
        if os.path.isfile(config.dbpath):
            os.remove(config.dbpath)
        app = create_app(config)

        cls.db = app.db.open()
        cls.app = app
        cls.config = config

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_query_db(self):
        self.db.conn.execute('INSERT INTO mentors \
                values ("Bryan Bugyi", "Python", "0")')
        self.db.conn.commit()
        query = self.db.query_db("SELECT * FROM mentors", one=True)
        self.assertEqual(query['name'], "Bryan Bugyi")
        self.assertEqual(query['keywords'], "Python")
        self.assertEqual(query['id'], 0)

    def test_pairMentor(self):
        postData = {'data': 'I need help with Python',
                    'user': 'bbugyi200',
                    'userid': '12345'}

        with self.app.test_client() as client:
            resp = client.post(self.config.serverurl + 'pairmentor', data=postData)
            self.assertEqual(json.loads(resp.data), postData)

    def test_askQuestion(self):
        from slackru.serverside import askQuestion
        self.assertEqual(0, askQuestion(self.db, "What's 2+2?", "bbugyi200", "12345"))
        self.assertEqual(1, askQuestion(self.db, "What's 2-2?", "bbugyi200", "12345"))
        self.assertEqual(2, askQuestion(self.db, "What's 2*2?", "bbugyi200", "12345"))

    def test_answerQuestion(self):
        pass


if __name__ == '__main__':
    unittest.main()
