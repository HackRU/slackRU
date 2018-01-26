import string
from slackru.tests import data


class SlackClient:
    """ SlackClient Testing Simulator """
    def __init__(self, api_key):
        pass

    def api_call(self, command, *args, **kwargs):
        return {'conversations.open': self.conversationsOpen,
                'chat.postMessage': self.chatPostMessage,
                'chat.delete': self.chatDelete}(*args, **kwargs)

    def conversationsOpen(self, users):
        return {'channel': {'id': data.channel[0]}}

    def chatPostMessage(self, channel, text, attachments=None, as_user=True):
        return {'ts': 'DUMMY TIMESTAMP'}

    def chatDelete(self, channel, timestamp, as_user=True):
        return self.defaultResp
