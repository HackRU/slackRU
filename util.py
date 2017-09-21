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
def grab_user(user:str) ->str:
    api = slack_client.api_call('users.list')
    if (api.get('ok')):
        users = api.get('members')
        for user in users:
            if 'name' in user and user.get('id') == use:
                return user['name']


'''
converts the username to an id
:param the username
'''
def username_to_id(username:str) -> str:
    api = slack_client.api_call('users.list')
    if api.get('ok'):
        users = api.get('members')
        for user in users:
            if 'id' in user and user['name'] == username:
                return user['id']

