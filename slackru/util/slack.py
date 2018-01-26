""" Slack Wrapper Functions """

import os

from slackclient import SlackClient


slack_client = SlackClient(os.environ['SLACK_API_KEY'])


# This exception is thrown when resp['ok'] is False
class SlackError(Exception): pass


def getDirectMessageChannel(users: 'str') -> 'str':
    resp = slack_client.api_call("conversations.open", users=users)
    return respErrorCheck(resp)['channel']['id']


def sendMessage(channel, text: 'str', attachments=None) -> '{str: ??}':
    resp = slack_client.api_call("chat.postMessage", channel=channel, text=text, attachments=attachments, as_user=True)
    return respErrorCheck(resp)


def deleteDirectMessages(channel: 'str', ts: 'str') -> '{str: ??}':
    resp = slack_client.api_call("chat.delete", channel=channel, ts=ts, as_user=True)
    return respErrorCheck(resp)


def respErrorCheck(resp: '{str: ??}') -> '{str: ??}':
    """ Slack Error Handling Wrapper """
    if resp['ok']:
        return resp
    else:
        raise SlackError(resp['error'])
