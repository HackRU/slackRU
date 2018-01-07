""" Slack Wrapper Functions """

import os

from slackclient import SlackClient


slack_client = SlackClient(os.environ['SLACK_API_KEY'])


def id_to_username(userid):
    api = slack_client.api_call('users.list')
    if (api.get('ok')):
        users = api.get('members')
        for user in users:
            if 'name' in user and user.get('id') == userid:
                return user['name']


def getDirectMessageChannel(users):
    try:
        resp = slack_client.api_call("conversations.open", users=users)
        return resp['channel']['id']
    except KeyError as e:
        raise KeyError(locals())


def sendMessage(channel, text, attachments=None):
    resp = slack_client.api_call("chat.postMessage", channel=channel, text=text, attachments=attachments, as_user=True)
    return resp


def deleteDirectMessages(channel, ts):
    slack_client.api_call("chat.delete", channel=channel, ts=ts, as_user=True)
