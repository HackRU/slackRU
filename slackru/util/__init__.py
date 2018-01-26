import os

if os.environ['SLACK_CONFIG'] == 'testing':
    from slackru.tests.slackclient import SlackClient
else:
    from slackclient import SlackClient

from slackru.util.slackapi import SlackAPI, SlackError


slack = SlackAPI(SlackClient(os.environ['SLACK_API_KEY']))
slack.SlackError = SlackError


def ifDebugThen(func, *args, inverted=False, **kwargs):
    """ Higher-Order Debugging Utility

    Calls function only if debugging is enabled.
    """
    from slackru.config import config
    if config.DEBUG ^ inverted:  # Bitwise XOR operator
        func(*args, **kwargs)


def ifNotDebugThen(func, *args, **kwargs):
    ifDebugThen(func, *args, inverted=True, **kwargs)
