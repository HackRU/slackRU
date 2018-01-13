""" Tests Flask Views (URL Routes) """

import json

import slackru.util as util

from slackru.tests import TestBase, params


class TestViews(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        from slackru.views import MessageActionView
        payload = cls.getPostData("yes", "mentorResponse_1")
        cls.MAVI = MessageActionView(payload)  # MAVI -> MessageActionViewInstance

    def setUp(self):
        self.db.drop_table('questions')
        self.db.create_questions()
        self.db.insertQuestion(self.data['question'][0], self.data['userid'][0], json.dumps([self.data['userid'][0]]))

    @params(('yes', 'mentorResponse_1'), ('no', 'mentorResponse_1'), ('yes', 'INVALID'))
    def test_message_action(self, value, callback):
        """ message_action Interface Test """
        from slackru.config import config
        postData = self.getPostData(value, callback)
        with self.app.test_client() as client:
            resp = client.post(config.serverurl + 'message_action', data=postData)
            self.assertEqual(200, resp.status_code)

    def test_mentorAccept(self):
        messageData = self.getMessageData()

        self.MAVI.mentorAccept()
        resp = util.slack.deleteDirectMessages(messageData[0]['channel'], messageData[0]['ts'])
        self.assertTrue(resp['ok'])

        with self.assertRaises(util.slack.SlackError):
            util.slack.deleteDirectMessages(messageData[1]['channel'], messageData[1]['ts'])

    def test_mentorDecline(self):
        messageData = self.getMessageData()

        self.MAVI.payLoad['message_ts'] = messageData[0]['ts']
        self.MAVI.mentorDecline()
        self.MAVI.threads['decline'].join()

        with self.assertRaises(KeyError):
            self.MAVI.thread_exceptions['decline']

        with self.assertRaisesRegex(util.slack.SlackError, 'message_not_found'):
            util.slack.deleteDirectMessages(messageData[0]['channel'], messageData[0]['ts'])

    @classmethod
    def getPostData(cls, value, callback):
        payload = {"actions": [{"name": "answer",
                                "value": value,
                                "type": "button"}],
                   "callback_id": callback,
                   "user": {'id': cls.data['mentorid'][0],
                            'name': cls.data['mentorname'][0]},
                   'message_ts': '111111111111',
                   'channel': {'id': cls.data['channel'][0],
                               'name': 'general'}}

        return {'payload': json.dumps(payload)}

    def getMessageData(self):
        Mdata = []
        self.db.drop_table('posts')
        self.db.create_posts()
        for mentorid in self.data['mentorid']:
            channel = util.slack.getDirectMessageChannel(mentorid)
            ts = util.slack.sendMessage(channel, "Test Message")['ts']

            self.db.insertPost(1, mentorid, channel, ts)

            Mdata.append({'channel': channel, 'ts': ts})

        return Mdata
