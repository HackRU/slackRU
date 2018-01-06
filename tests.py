""" This module is used to run the SlackRU UnitTests

usage: python tests.py
"""

import os
import sys
import unittest

os.environ['SLACK_CONFIG'] = 'development'
from slackru.config import config

loader = unittest.TestLoader()
runner = unittest.runner.TextTestRunner(verbosity=2)
suite = loader.discover(os.path.dirname(os.path.realpath(__file__)) + '/slackru/tests')


if __name__ == "__main__":
    sys.stdout = open(config.logpath, 'w')

    runner.run(suite)

    sys.stdout.close()
    sys.stdout = sys.__stdout__

    logfile = open(config.logpath, 'r')
    print('\n======= ' + os.path.basename(config.logpath) + ' =======\n' + logfile.read())
