#!/usr/bin/env python3

""" Used to run the SlackRU UnitTests

    usage:
        ./runtests.py -h
"""

import os
import unittest
import argparse

loader = unittest.TestLoader()
runner = unittest.runner.TextTestRunner(verbosity=2, buffer=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    pattern_opts = {'all': 'test*.py',
                    'slackbot': 'test*bot*.py',
                    'views': 'test_*view*.py'}

    parser.add_argument('test_suite', nargs='?', choices=[key for key in pattern_opts.keys()], default='all')
    args = parser.parse_args()

    suite = loader.discover(os.path.dirname(os.path.realpath(__file__)) + '/slackru/tests',
                                            pattern=pattern_opts[args.test_suite])
    runner.run(suite)
