from unittest.mock import MagicMock


def side_effect(action, *args, **kwargs):
    return {'channel': {'id': 'CHANNEL_ID'},
            'ts': 'TIMESTAMP',
            'ok': True}


slack_mock = MagicMock()
slack_mock.api_call = MagicMock(side_effect=side_effect)
