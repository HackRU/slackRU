'''
This file contains util methods that we can use
'''
from slackclient import SlackClient
import config

slack_client = SlackClient(config.apiT)
slack_web_client = SlackClient(config.oauthT)
'''
converts an id to usernamae
:param the user id to convert
'''
def grab_user(user):
    api = slack_client.api_call('users.list')
    if (api.get('ok')):
        users = api.get('members')
        for user in users:
            if 'name' in user and user.get('id') == use:
                return user['name']
