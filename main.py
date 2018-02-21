#!/usr/bin/env python3

""" Use this script to manually run the server OR slackbot.

    usage:
        ./main.py -h
"""

import os
import argparse


def server():
    from slackru import create_app
    app = create_app()
    app.run()


def slackbot():
    from slackru.bot.slackbot import SlackBot
    bot = SlackBot()
    bot.run()


if __name__ == "__main__":
    runtype_opts = {'server': server, 'slackbot': slackbot}

    description = __doc__.split('\n')[0]  # First line of this module's docstring
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('runtype', nargs='?', choices=[key for key in runtype_opts.keys()], default='server', help="run 'server' or 'slackbot'")
    parser.add_argument('--config', dest='config', choices=['development', 'production', 'testing'], default='development', help="set configuration class (default is 'development')")
    args = parser.parse_args()

    os.environ['SLACK_CONFIG'] = args.config

    runtype_opts[args.runtype]()
