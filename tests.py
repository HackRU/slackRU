""" This module is used to run the SlackRU UnitTests

    usage:
        python tests.py
"""

import os
import sys
import unittest

logPath = '/var/tmp/slackru.log'

loader = unittest.TestLoader()
runner = unittest.runner.TextTestRunner(verbosity=2)
suite = loader.discover(os.path.dirname(os.path.realpath(__file__)) + '/slackru/tests')


if __name__ == "__main__":
    sys.stdout = open(logPath, 'w')

    runner.run(suite)

    sys.stdout.close()
    sys.stdout = sys.__stdout__

    logfile = open(logPath, 'r')
    print('\n======= STDOUT =======\n' + logfile.read())
