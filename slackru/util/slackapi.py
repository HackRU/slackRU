""" Slack API Wrapper """


# This exception is thrown when resp['ok'] is False
class SlackError(Exception): pass


def slack_error_check(func):
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        if resp['ok']:
            return resp
        else:
            raise SlackError(resp['error'])
    return wrapper


class SlackAPI:
    def __init__(self, slack_client):
        self.api_call = slack_error_check(slack_client.api_call)
        self.client = slack_client
        self.SlackError = SlackError  # Easy Access for Tests

    def getDirectMessageChannel(self, users):
        resp = self.api_call("conversations.open", users=users)
        return resp['channel']['id']

    def sendMessage(self, channel, text, attachments=None):
        resp = self.api_call("chat.postMessage", channel=channel, text=text, attachments=attachments, as_user=True)
        return resp['ts']

    def deleteDirectMessages(self, channel, ts):
        resp = self.api_call("chat.delete", channel=channel, ts=ts, as_user=True)
        return resp
