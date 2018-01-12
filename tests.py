""" Used to run the SlackRU UnitTests

    usage:
        python tests.py -h
"""

import os
import unittest
import argparse


pattern_opts = {'all': 'test*.py',
                'slackbot': 'test*bot*.py',
                'views': 'test_*view*.py'}

parser = argparse.ArgumentParser()
parser.add_argument('test_suite', nargs='?', choices=[key for key in pattern_opts.keys()], default='all')
args = parser.parse_args()

loader = unittest.TestLoader()
runner = unittest.runner.TextTestRunner(verbosity=2, buffer=True)


suite = loader.discover(os.path.dirname(os.path.realpath(__file__)) + '/slackru/tests',
                                        pattern=pattern_opts[args.test_suite])


if __name__ == "__main__":
    runner.run(suite)
