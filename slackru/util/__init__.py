from slackclient import SlackClient

from slackru.util.slackapi import SlackAPI
from slackru.config import config

slack_client = SlackClient(config.slack_api_key)
slack = SlackAPI(slack_client)


def ifTestingThen(func, *args, inverted=False, **kwargs):
    """ Higher-Order Testing Utility

    Calls function only if testing is enabled.
    """
    if config.TESTING ^ inverted:  # Bitwise XOR operator
        func(*args, **kwargs)


def ifNotTestingThen(func, *args, **kwargs):
    ifTestingThen(func, *args, inverted=True, **kwargs)
