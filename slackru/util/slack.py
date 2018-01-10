""" Slack Wrapper Functions """

import os

from slackclient import SlackClient


slack_client = SlackClient(os.environ['SLACK_API_KEY'])


class SlackError(Exception): pass


def id_to_username(userid):
    resp = slack_client.api_call('users.list')
    users = respErrorCheck(resp)['members']
    for user in users:
        if 'name' in user and user['id'] == userid:
            return user['name']


def openConversation(users):
    resp = slack_client.api_call("conversations.open", users=users)
    return respErrorCheck(resp)


def sendMessage(channel, text, attachments=None):
    resp = slack_client.api_call("chat.postMessage", channel=channel, text=text, attachments=attachments, as_user=True)
    return respErrorCheck(resp)


def deleteDirectMessages(channel, ts):
    resp = slack_client.api_call("chat.delete", channel=channel, ts=ts, as_user=True)
    return respErrorCheck(resp)


def respErrorCheck(resp):
    if resp['ok']:
        return resp
    else:
        raise SlackError(resp['error'])
