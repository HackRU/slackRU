#!/usr/bin/env python3

""" Used to run the SlackRU UnitTests

    usage:
        ./runtests.py -h
"""

import os
import argparse
import unittest
from unittest.mock import MagicMock, patch

from slackru.tests import slack_mock
from slackru.util.slackapi import SlackAPI


loader = unittest.TestLoader()
runner = unittest.runner.TextTestRunner(verbosity=2, buffer=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    pattern_opts = {'all': 'test*.py',
                    'slackbot': 'test*bot*.py',
                    'views': 'test_*view*.py'}

    parser.add_argument('test_suite', nargs='?', choices=[key for key in pattern_opts.keys()], default='all', help="set of tests to run (default is 'all')")
    parser.add_argument('--no-mock', dest='mock', action='store_false', help="disable mock objects from overwriting original objects (they will wrap original objects instead)")
    args = parser.parse_args()

    if not args.mock:
        from slackru.util import slack_client
        slack_mock.api_call = MagicMock(wraps=slack_client.api_call)

    suite = loader.discover(os.path.dirname(os.path.realpath(__file__)) + '/slackru/tests',
                                            pattern=pattern_opts[args.test_suite])

    with patch('slackru.util.slack', SlackAPI(slack_mock)):
        runner.run(suite)
