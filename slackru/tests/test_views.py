""" Tests Flask Views (URL Routes) """

import json

import slackru.util as util
from slackru.tests import TestBase, params, data
from slackru.tests import slack_mock


class TestViews(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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
        self.db.drop_table('posts')
        self.db.create_posts()
        for mentorid in data['mentorid']:
            channel = util.slack.getDirectMessageChannel(mentorid)
            ts = util.slack.sendMessage(channel, "Test Message")

            self.db.insertPost(1, mentorid, channel, ts)

            Mdata.append({'channel': channel, 'ts': ts})

        slack_mock.reset_mock()
        return Mdata
