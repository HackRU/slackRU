'''
This file contains util methods that we can use
'''
from slackclient import SlackClient
from . import config

slack_client = SlackClient(config.apiT)
slack_web_client = SlackClient(config.oauthT)


def grab_user(use: str) -> str:
    """
        converts an id to usernamae
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


def message(channelid: str, message: str) -> None:
    """
        Util Function to send a message
    """
    slack_client.api_call("chat.postMessage", channel=channelid, text=message, as_user=True)
