""" Used to run the SlackRU UnitTests

    usage:
        python runtests.py -h
"""

import os
import sys
import unittest
import argparse

loader = unittest.TestLoader()
runner = unittest.runner.TextTestRunner(verbosity=2, buffer=True)


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    pattern_opts = {'all': 'test*.py',
                    'slackbot': 'test*bot*.py',
                    'views': 'test_*view*.py'}

    parser.add_argument('test_suite', nargs='?', choices=[key for key in pattern_opts.keys()], default='all')
    parser.add_argument('--disable-stdout', type=str2bool, dest='disable_stdout', default=True)
    args = parser.parse_args()

    if args.disable_stdout:
        sys.stdout = open(os.devnull, 'w')

    suite = loader.discover(os.path.dirname(os.path.realpath(__file__)) + '/slackru/tests',
                                            pattern=pattern_opts[args.test_suite])
    runner.run(suite)
