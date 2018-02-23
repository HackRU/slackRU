""" Tests Flask Views (URL Routes) """

import json

import slackru.util as util
from slackru import get_db
from slackru.tests import TestBase, reset_mock, params, data
from slackru.tests import slack_mock
from slackru.config import config


class TestViews(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from slackru.views import MessageActionView
        payload = cls.getPostData("yes", "mentorResponse_1")
        cls.MAVI = MessageActionView(payload)  # MAVI -> MessageActionViewInstance

        cls.db = get_db()

        cls.db.drop_all()
        cls.db.create_all()
        cls.db.session.commit()

        cls.db.insertMentor(data['mentor'][0], data['mentorname'][0], data['mentorid'][0], data['phone_number'][0], "Python")
        cls.db.insertMentor(data['mentor'][1], data['mentorname'][1], data['mentorid'][1], data['phone_number'][1], "Java")

        cls.db.insertQuestion(data['question'][0], data['userid'][0], json.dumps([data['userid'][0]]))

    def setUp(self):
        super().setUp()

    @params(('Party Pam', '987654321', 'HTML,CSS'))
    def test_register_mentor(self, fullname, phone_number, keywords):
        postData = {'fullname': fullname,
                    'phone_number': phone_number,
                    'keywords': keywords,
                    'userid': data['userid'][0],
                    'username': data['username'][0]}

        with self.app.test_client() as client:
            resp = client.post(config.serverurl + 'register_mentor', data=postData)
            self.assertEqual(200, resp.status_code)

    @params(('yes', 'mentorResponse_1'), ('no', 'mentorResponse_1'), ('yes', 'INVALID'))
    def test_message_action(self, value, callback):
        """ message_action Interface Test """
        postData = self.getPostData(value, callback)
        with self.app.test_client() as client:
            resp = client.post(config.serverurl + 'message_action', data=postData)
            self.assertEqual(200, resp.status_code)

    @params(("My Java code is not working", [0,1]), ("Anyone know python?", [0,1]), ("Can someone help me?", [0,1]))
    def test_pair_mentor(self, question, mentorIndexes):
        postData = {'question': question,
                    'userid': data['userid'][0]}
        with self.app.test_client() as client:
            resp = client.post(config.serverurl + 'pair_mentor', data=postData)
            self.assertEqual(resp.headers['mentorIDs'], str([data['mentorid'][i] for i in mentorIndexes]))

    @reset_mock
    def test_mentorAccept(self):
        self.getMessageData()
        self.MAVI.mentorAccept()
        self.MAVI.threads['accept'].join()
        self.assertEqual([call[1][0] for call in slack_mock.method_calls],
                         ['chat.delete', 'conversations.open', 'chat.postMessage'])

    def test_mentorDecline(self):
        messageData = self.getMessageData()
        self.MAVI.payLoad['message_ts'] = messageData[0]['ts']
        self.MAVI.mentorDecline()
        self.MAVI.threads['decline'].join()

        with self.assertRaises(KeyError):
            self.MAVI.thread_exceptions['decline']

    @classmethod
    def getPostData(cls, value, callback):
        payload = {"actions": [{"name": "answer",
                                "value": value,
                                "type": "button"}],
                   "callback_id": callback,
                   "user": {'id': data['mentorid'][0],
                            'name': data['mentorname'][0]},
                   'message_ts': '111111111111',
                   'channel': {'id': data['channel'][0],
                               'name': 'general'}}

        return {'payload': json.dumps(payload)}

    def getMessageData(self):
        Mdata = []
        self.db.Post.query.delete()
        for mentorid in data['mentorid']:
            channel = util.slack.getDirectMessageChannel(mentorid)
            ts = util.slack.sendMessage(channel, "Test Message")

            self.db.insertPost(1, mentorid, channel, ts)

            Mdata.append({'channel': channel, 'ts': ts})

        slack_mock.reset_mock()
        return Mdata
