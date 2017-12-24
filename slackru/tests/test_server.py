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
                values ("Bryan Bugyi", "Python", "+16095007081")')
        self.db.conn.commit()
        query = self.db.query_db("SELECT * FROM mentors", one=True)
        self.assertEqual(query['name'], "Bryan Bugyi")
        self.assertEqual(query['keywords'], "Python")
        self.assertEqual(query['phone'], "+16095007081")

    def test_pairMentor(self):
        postData = {'data': 'I need help with Python',
                    'user': 'bbugyi200',
                    'userid': '12345'}

        with self.app.test_client() as client:
            resp = client.post(self.config.serverurl + 'pairmentor', data=postData)
            self.assertEqual(json.loads(resp.data), postData)


if __name__ == '__main__':
    unittest.main()
