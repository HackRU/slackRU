import unittest
import flask
from ..serverside import query_db, createApp


class TestServer(unittest.TestCase):
    def setUp(self):
        self.app = createApp(debug=True)

    def test_query_db(self):
        self.assertEqual(query_db('SELECT * FROM mentors;'),
                         [("Bryan Bugyi", "Python", "+16095007081")])

    def test_pairMentor(self):
        postData = {}
        postData['data'] = "mentors"
        postData['user'] = "bbugyi200"
        postData['userid'] = "11111111"
        with self.app.test_request_context('/pairmentor', method='POST', data=postData):
            self.assertEqual(flask.request.form.to_dict(), postData)


if __name__ == '__main__':
    unittest.main()
