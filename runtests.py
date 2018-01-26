""" Used to run the SlackRU UnitTests

    usage:
        python runtests.py -h
"""

import os
import sys
import unittest
import argparse

os.environ['SLACK_CONFIG'] = 'testing'

loader = unittest.TestLoader()
runner = unittest.runner.TextTestRunner(verbosity=2, buffer=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    pattern_opts = {'all': 'test*.py',
                    'slackbot': 'test*bot*.py',
                    'views': 'test_*view*.py'}

    parser.add_argument('test_suite', nargs='?', choices=[key for key in pattern_opts.keys()], default='all')
    args = parser.parse_args()

    sys.stdout = sys.stderr = open(os.devnull, 'w')

    suite = loader.discover(os.path.dirname(os.path.realpath(__file__)) + '/slackru/tests',
                                            pattern=pattern_opts[args.test_suite])
    runner.run(suite)
