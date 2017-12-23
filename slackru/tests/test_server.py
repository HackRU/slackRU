import os
import unittest
from slackru.config import getConfig
from slackru import create_app
from ..serverside import query_db


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = getConfig['testing']
        if os.path.isfile(config.dbpath):
            os.remove(config.dbpath)
        cls.app = create_app(config)
        cls.db = cls.app.database
        cls.config = config

    def test_query_db(self):
        self.db.conn.execute('INSERT INTO mentors \
                values ("Bryan Bugyi", "Python", "+16095007081")')
        self.db.conn.commit()
        self.assertEqual(query_db(self.db, 'SELECT * FROM mentors;'),
                         [("Bryan Bugyi", "Python", "+16095007081")])

    def test_pairMentor(self):
        postData = {}
        postData['data'] = "mentors"
        postData['user'] = "bbugyi200"
        postData['userid'] = "11111111"

        with self.app.test_request_context('/pairmentor', method='POST', data=postData):
            from slackru import views
            resp = views.pairMentor()
            self.assertEqual(resp, postData)


if __name__ == '__main__':
    unittest.main()
