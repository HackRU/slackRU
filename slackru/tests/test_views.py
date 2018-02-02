""" Tests Flask Views (URL Routes) """

import json

import slackru.util as util

from slackru.tests import TestBase, params, data
from slackru.tests.slack_mock import slack_mock


class TestViews(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.messageData = cls.getMessageData()
        from slackru.views import MessageActionView
        payload = cls.getPostData("yes", "mentorResponse_1")
        cls.MAVI = MessageActionView(payload)  # MAVI -> MessageActionViewInstance

    def setUp(self):
        super().setUp()
        self.db.drop_table('questions')
        self.db.create_questions()
        self.db.insertQuestion(data['question'][0], data['userid'][0], json.dumps([data['userid'][0]]))

    @params(('yes', 'mentorResponse_1'), ('no', 'mentorResponse_1'), ('yes', 'INVALID'))
    def test_message_action(self, value, callback):
        """ message_action Interface Test """
        from slackru.config import config
        postData = self.getPostData(value, callback)
        with self.app.test_client() as client:
            resp = client.post(config.serverurl + 'message_action', data=postData)
            self.assertEqual(200, resp.status_code)

    def test_mentorAccept(self):
        self.MAVI.mentorAccept()
        self.assertEqual([call[1][0] for call in slack_mock.method_calls],
                         ['chat.delete', 'conversations.open', 'chat.postMessage'])

    def test_mentorDecline(self):
        self.MAVI.payLoad['message_ts'] = self.messageData[0]['ts']
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

    @classmethod
    def getMessageData(cls):
        Mdata = []
        cls.db.drop_table('posts')
        cls.db.create_posts()
        for mentorid in data['mentorid']:
            channel = util.slack.getDirectMessageChannel(mentorid)
            ts = util.slack.sendMessage(channel, "Test Message")

            cls.db.insertPost(1, mentorid, channel, ts)

            Mdata.append({'channel': channel, 'ts': ts})

        return Mdata
