import os
from slackclient import SlackClient


slack_client = SlackClient(os.environ['SLACK_API_KEY'])


def grab_user(use: str) -> str:
    """
        converts an id to username
        :param the user id to convert
    """
    api = slack_client.api_call('users.list')
    if (api.get('ok')):
        users = api.get('members')
        for user in users:
            if 'name' in user and user.get('id') == use:
                return user['name']


def username_to_id(username: str) -> str:
    """
        converts the username to an id
        :param the username
    """
    api = slack_client.api_call('users.list')
    if api.get('ok'):
        users = api.get('members')
        for user in users:
            if 'id' in user and user['name'] == username:
                return user['id']


def getDirectMessageChannel(userid: str) -> str:
    resp = slack_client.api_call("conversations.open", users=userid)
    return resp['channel']['id']


def message(channelid: str, message: str) -> None:
    """ Util Function to send a message """
    resp = slack_client.api_call("chat.postMessage", channel=channelid, text=message, as_user=True)
    return resp['ts']


def deleteDirectMessages(channel, ts):
    slack_client.api_call("chat.delete", channel=channel, ts=ts, as_user=True)
