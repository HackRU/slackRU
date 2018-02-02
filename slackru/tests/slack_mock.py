from unittest.mock import Mock

import slackru.util
from slackru.util.slackapi import SlackAPI


def side_effect(action, *args, **kwargs):
    return {'channel': {'id': 'CHANNEL_ID'},
            'ts': 'TIMESTAMP',
            'ok': True}


slack_mock = Mock()
slack_mock.api_call = Mock(side_effect=side_effect)
slackru.util.slack = SlackAPI(slack_mock)
